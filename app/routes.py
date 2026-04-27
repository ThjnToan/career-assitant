from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models import Application, Interview, Contact, Activity
from app.utils import (
    parse_job_description, generate_tailoring_suggestions, generate_weekly_report,
    get_status_color, VALID_STATUSES
)
import json
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    now = datetime.utcnow()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
    
    # Weekly progress
    apps_this_week = Application.query.filter(
        Application.user_id == current_user.id,
        Application.applied_date >= week_start
    ).count()
    
    # Pipeline
    pipeline = {}
    for app in Application.query.filter_by(user_id=current_user.id).all():
        pipeline[app.status] = pipeline.get(app.status, 0) + 1
    
    total = sum(pipeline.values())
    active = total - pipeline.get('Rejected', 0) - pipeline.get('Accepted', 0) - pipeline.get('Withdrawn', 0) - pipeline.get('Ghosted', 0)
    
    # Upcoming interviews
    upcoming_interviews = Interview.query.join(Application).filter(
        Application.user_id == current_user.id,
        Interview.scheduled_date >= now,
        Interview.status == 'Scheduled'
    ).order_by(Interview.scheduled_date.asc()).limit(5).all()
    
    # Overdue follow-ups
    overdue = Application.query.filter(
        Application.user_id == current_user.id,
        Application.follow_up_date < now,
        Application.status.in_(['Applied', 'Phone Screen', 'Technical Screen', 'Interview Round 1', 'Interview Round 2', 'Interview Round 3', 'Final Round'])
    ).order_by(Application.follow_up_date.asc()).all()
    
    # Recent activity
    recent_activity = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.created_at.desc()).limit(5).all()
    
    # Today's interviews
    today_start = now.replace(hour=0, minute=0, second=0)
    today_end = now.replace(hour=23, minute=59, second=59)
    today_interviews = Interview.query.join(Application).filter(
        Application.user_id == current_user.id,
        Interview.scheduled_date.between(today_start, today_end),
        Interview.status == 'Scheduled'
    ).all()
    
    return render_template('dashboard.html',
        user=current_user,
        apps_this_week=apps_this_week,
        pipeline=pipeline,
        total=total,
        active=active,
        upcoming_interviews=upcoming_interviews,
        overdue=overdue,
        recent_activity=recent_activity,
        today_interviews=today_interviews,
        week_start=week_start,
        now=now
    )

@main_bp.route('/applications')
@login_required
def applications():
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    
    query = Application.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(
            db.or_(
                Application.company.ilike(f'%{search}%'),
                Application.role.ilike(f'%{search}%'),
                Application.notes.ilike(f'%{search}%')
            )
        )
    
    apps = query.order_by(Application.last_updated.desc()).all()
    statuses = VALID_STATUSES
    
    return render_template('applications.html', applications=apps, statuses=statuses, current_status=status_filter, search=search)

@main_bp.route('/applications/new', methods=['GET', 'POST'])
@login_required
def new_application():
    if request.method == 'POST':
        app = Application(
            user_id=current_user.id,
            company=request.form['company'].strip(),
            role=request.form['role'].strip(),
            location=request.form.get('location', '').strip(),
            salary_range=request.form.get('salary_range', '').strip(),
            job_url=request.form.get('job_url', '').strip(),
            description=request.form.get('description', '').strip(),
            source=request.form.get('source', '').strip(),
            notes=request.form.get('notes', '').strip(),
            follow_up_date=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(app)
        db.session.commit()
        
        activity = Activity(
            user_id=current_user.id,
            activity_type='Application Created',
            entity_type='application',
            entity_id=app.id,
            description=f"Applied to {app.company} for {app.role}"
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Application to {app.company} logged!', 'success')
        return redirect(url_for('main.applications'))
    
    return render_template('application_form.html', application=None, statuses=VALID_STATUSES)

@main_bp.route('/applications/<int:id>')
@login_required
def application_detail(id):
    app = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    interviews = Interview.query.filter_by(application_id=id).order_by(Interview.round_num.asc()).all()
    return render_template('application_detail.html', application=app, interviews=interviews, statuses=VALID_STATUSES)

@main_bp.route('/applications/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_application(id):
    app = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        old_status = app.status
        app.company = request.form['company'].strip()
        app.role = request.form['role'].strip()
        app.location = request.form.get('location', '').strip()
        app.salary_range = request.form.get('salary_range', '').strip()
        app.job_url = request.form.get('job_url', '').strip()
        app.description = request.form.get('description', '').strip()
        app.source = request.form.get('source', '').strip()
        app.notes = request.form.get('notes', '').strip()
        app.status = request.form.get('status', 'Applied')
        app.last_updated = datetime.utcnow()
        db.session.commit()
        
        if old_status != app.status:
            activity = Activity(
                user_id=current_user.id,
                activity_type='Status Updated',
                entity_type='application',
                entity_id=app.id,
                description=f"{app.company} ({app.role}): {old_status} -> {app.status}"
            )
            db.session.add(activity)
            db.session.commit()
            flash('Status updated!', 'success')
        else:
            flash('Application updated!', 'success')
        
        return redirect(url_for('main.application_detail', id=id))
    
    return render_template('application_form.html', application=app, statuses=VALID_STATUSES)

@main_bp.route('/applications/<int:id>/delete', methods=['POST'])
@login_required
def delete_application(id):
    app = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(app)
    db.session.commit()
    flash('Application deleted.', 'info')
    return redirect(url_for('main.applications'))

@main_bp.route('/applications/<int:id>/interviews/new', methods=['POST'])
@login_required
def new_interview(id):
    app = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    scheduled_date = request.form.get('scheduled_date')
    if scheduled_date:
        scheduled_date = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00').replace('+00:00', ''))
    
    iv = Interview(
        application_id=id,
        interview_type=request.form.get('interview_type', 'Phone Screen'),
        scheduled_date=scheduled_date or datetime.utcnow(),
        duration_minutes=int(request.form.get('duration', 60)),
        interviewer_name=request.form.get('interviewer_name', '').strip(),
        interviewer_title=request.form.get('interviewer_title', '').strip(),
        location=request.form.get('location', '').strip(),
        video_link=request.form.get('video_link', '').strip(),
        notes=request.form.get('notes', '').strip()
    )
    db.session.add(iv)
    db.session.commit()
    
    activity = Activity(
        user_id=current_user.id,
        activity_type='Interview Scheduled',
        entity_type='interview',
        entity_id=iv.id,
        description=f"{iv.interview_type} for {app.company} on {iv.scheduled_date.strftime('%Y-%m-%d')}"
    )
    db.session.add(activity)
    db.session.commit()
    
    flash('Interview scheduled!', 'success')
    return redirect(url_for('main.application_detail', id=id))

@main_bp.route('/interviews')
@login_required
def interviews():
    now = datetime.utcnow()
    upcoming = Interview.query.join(Application).filter(
        Application.user_id == current_user.id,
        Interview.scheduled_date >= now,
        Interview.status == 'Scheduled'
    ).order_by(Interview.scheduled_date.asc()).all()
    
    past = Interview.query.join(Application).filter(
        Application.user_id == current_user.id,
        Interview.scheduled_date < now
    ).order_by(Interview.scheduled_date.desc()).limit(20).all()
    
    return render_template('interviews.html', upcoming=upcoming, past=past)

@main_bp.route('/pipeline')
@login_required
def pipeline():
    pipeline_data = {}
    for app in Application.query.filter_by(user_id=current_user.id).all():
        pipeline_data[app.status] = pipeline_data.get(app.status, 0) + 1
    
    total = sum(pipeline_data.values())
    active = total - pipeline_data.get("Rejected", 0) - pipeline_data.get("Accepted", 0) - pipeline_data.get("Withdrawn", 0) - pipeline_data.get("Ghosted", 0)
    
    return render_template('pipeline.html', pipeline=pipeline_data, total=total, active=active)

@main_bp.route('/followups')
@login_required
def followups():
    now = datetime.utcnow()
    overdue = Application.query.filter(
        Application.user_id == current_user.id,
        Application.follow_up_date < now,
        Application.status.in_(['Applied', 'Phone Screen', 'Technical Screen', 'Interview Round 1', 'Interview Round 2', 'Interview Round 3', 'Final Round'])
    ).order_by(Application.follow_up_date.asc()).all()
    
    return render_template('followups.html', followups=overdue)

@main_bp.route('/parser', methods=['GET', 'POST'])
@login_required
def parser_page():
    result = None
    suggestions = None
    if request.method == 'POST':
        text = request.form.get('job_description', '')
        if text:
            result = parse_job_description(text)
            suggestions = generate_tailoring_suggestions(text)
    return render_template('parser.html', result=result, suggestions=suggestions)

@main_bp.route('/report')
@login_required
def report():
    report_data = generate_weekly_report(current_user)
    return render_template('report.html', report=report_data)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', '').strip()
        current_user.email = request.form.get('email', '').strip().lower()
        current_user.title = request.form.get('title', '').strip()
        current_user.location = request.form.get('location', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.linkedin = request.form.get('linkedin', '').strip()
        current_user.portfolio = request.form.get('portfolio', '').strip()
        current_user.weekly_apps_goal = int(request.form.get('weekly_apps_goal', 5))
        current_user.weekly_net_goal = int(request.form.get('weekly_net_goal', 2))
        current_user.target_roles = request.form.get('target_roles', '').strip()
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html', user=current_user)

@main_bp.route('/api/stats')
@login_required
def api_stats():
    now = datetime.utcnow()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
    
    pipeline = {}
    for app in Application.query.filter_by(user_id=current_user.id).all():
        pipeline[app.status] = pipeline.get(app.status, 0) + 1
    
    total = sum(pipeline.values())
    active = total - pipeline.get('Rejected', 0) - pipeline.get('Accepted', 0) - pipeline.get('Withdrawn', 0) - pipeline.get('Ghosted', 0)
    
    apps_this_week = Application.query.filter(
        Application.user_id == current_user.id,
        Application.applied_date >= week_start
    ).count()
    
    upcoming_count = Interview.query.join(Application).filter(
        Application.user_id == current_user.id,
        Interview.scheduled_date >= now,
        Interview.status == 'Scheduled'
    ).count()
    
    return jsonify({
        'total': total,
        'active': active,
        'offers': pipeline.get('Offer', 0) + pipeline.get('Negotiating', 0) + pipeline.get('Accepted', 0),
        'this_week': apps_this_week,
        'upcoming_interviews': upcoming_count,
        'pipeline': pipeline
    })
