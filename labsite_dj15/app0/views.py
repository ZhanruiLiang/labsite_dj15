# -*- encoding=utf-8 -*-
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import login as _login, logout as _logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urljoin
from time import sleep
import functools
import datetime
import json
import spec
import logging
import os
import codecs
import traceback

from upload import UploadForm, Submission, Score, ScoreForm,  upload as _upload
from check import check_submission, Decompression, Compilation
from nav import render_nav_html
from errors import *
import account
import grade as grade_

logger = logging.getLogger(__name__)

pjoin = os.path.join

def wrap_json(view):
    @functools.wraps(view)
    def new_view(request, *args, **kwargs):
        json = view(request, *args, **kwargs)
        return HttpResponse(json, 'json')
    return new_view

# DEBUG purpose only
def make_test_view(template_name):
    def view(request):
        return make_response(request, template_name, {})
    return view

def test_upload(request):
    if request.method == 'GET':
        form = UploadForm()
        msg = 'Please upload a txt file'
    elif request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            msg = file.read()
    return make_response(request, 'test_upload.html', {
        'form': form,
        'msg': msg,
        })

def ajax_date(request):
    if request.is_ajax():
        return json.dumps(str(datetime.datetime.today()))

def make_response(request, templateName, contextDict):
    if 'nav' not in contextDict:
        contextDict['nav'] = render_nav_html(request.user)
    return HttpResponse(get_template(templateName).render(
        RequestContext(request, contextDict)))

def error_response(request, msg):
    return make_response(request, 'error.html', {
        'error': msg,
        'next': request.path,
        })

login_required = login_required(login_url=settings.LOGIN_URL)

def usertype_only(type):
    def deco(view):
        @functools.wraps(view)
        @login_required
        def new_view(request, *args, **kwargs):
            user = request.user
            return view(request, *args, **kwargs)
            if user.usertype == type:
                return view(request, *args, **kwargs)
            else:
                return make_response(request, 'error.html', {
                    'error': 'Permission deny!',
                    })
        return new_view
    return deco

@csrf_protect
@never_cache
def register(request):
    # If request is a GET, show page. If is a POST method, do register.
    if request.method == 'GET':
        form = account.RegisterForm()
        return make_response(request, 'register.html', {
            'form': form,
            'next': request.GET.get('next', settings.LOGIN_REDIRECT_URL),
            })
    elif request.method == 'POST':
        form = account.RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.usertype = 'student'
            user.save()
            return HttpResponseRedirect(request.POST.get('next', settings.LOGIN_REDIRECT_URL))
        return make_response(request, 'register.html', {
            'form': form,
            'next': request.POST.get('next', settings.LOGIN_REDIRECT_URL),
            })

@csrf_protect
@never_cache
def login(request):
    redirect_to = settings.LOGIN_REDIRECT_URL
    if request.method == 'GET':
        redirect_to = request.GET.get('next', redirect_to)
    elif request.method == 'POST':
        redirect_to = request.POST.get('next', redirect_to)
    return _login(request, template_name='login.html', 
            authentication_form=account.LoginForm,
            extra_context={'next': redirect_to, 'nav': render_nav_html(request.user)},
            )

@login_required
def show_ass(request, assID=None):
    if assID:
        assignment = spec.Assignment.objects.get(id=assID)
        return make_response(request, 'ass.html', {
            'ass': assignment, 
            'form': UploadForm(),
            })
    else:
        asss = spec.Assignment.objects.all()
        return make_response(request, 'ass_list.html', {
            'datas': [(ass, ass.is_submitted(request.user)) for ass in asss],
            })

@csrf_protect
@usertype_only('TA')
def post_ass(request):
    if request.method == 'GET':
        form = spec.AssignmentCreationForm()
        redirect_to = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        return make_response(request, 'addass.html', {
            'form': form,
            'next': redirect_to,
            })
    elif request.method == 'POST':
        form = spec.AssignmentCreationForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            success, msg = spec.make_ass_dir(assignment)
            if success:
                assignment.save()
                redirect_to = urljoin(settings.ASSIGNMENT_URL, str(assignment.id))
                return HttpResponseRedirect(redirect_to)
            else:
                return error_response(request, msg)
        return make_response(request, 'addass.html', {
            'form': form,
            'next': request.POST['next'],
            })

@csrf_protect
@usertype_only('TA')
def edit_ass(request, assID):
    if request.method == 'GET':
        assignment = spec.Assignment.objects.get(id=assID)
        form = spec.AssignmentModifyForm(instance=assignment)
        return make_response(request, 'editass.html', {
            'form': form,
            'next': request.GET.get('next', settings.LOGIN_REDIRECT_URL),
            })
    elif request.method == 'POST':
        assignment = spec.Assignment.objects.get(id=assID)
        form = spec.AssignmentModifyForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            success, msg = spec.make_ass_dir(assignment)
            if success:
                assignment = form.save()
                redirect_to = urljoin(settings.ASSIGNMENT_URL, str(assignment.id))
                return HttpResponseRedirect(redirect_to)
            else:
                return error_response(request, msg)
        return make_response(request, 'editass.html', {
            'form': form,
            'next': request.GET['next'],
            })

@login_required
def logout(request):
    return _logout(request, next_page=settings.LOGOUT_REDIRECT_URL, 
            template_name='logout.html')

@login_required
def profile(request, userID=None):
    # show a user's profile
    pass

def home(request):
    return make_response(request, 'home.html', {})

@wrap_json
@usertype_only('student')
def upload(request):
    # upload/make a submission
    if request.method == 'POST':
        sleep(1)
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            assID = request.POST['assID']
            user = request.user
            submission = None
            try:
                submission = _upload(user, assID, file)
                check_submission(submission)
                submission.retcode = 0
                submission.message = 'success'
                submission.save()
                return json.dumps({
                    'code': 0,
                    'message': submission.message,
                    'sid': str(submission.id),
                    })
            except UploadError as err:
                html = err.html()
                if submission:
                    submission.code = err.code
                    submission.message = html
                    submission.save()
                result = json.dumps({
                    'code': err.code,
                    'message': html,
                    })
                logger.debug('code:{}\nhtml:{}'.format(err.code, html.encode('utf8')))
                return result
        return json.dumps({
            'code': 1,
            'message': form.errors,
            })
    return json.dumps({
        'code': 1,
        'message': 'method is not POST',
        })

@wrap_json
@login_required
def submission_list(request, assID=None):
    # list a user's submissions for the assignment
    user = request.user
    if assID is not None:
        assignment = spec.Assignment.objects.get(id=assID)
        submissions = assignment.submission_set
    else:
        submissions = Submission.objects
    if request.user.usertype == 'student':
        submissions = submissions.filter(user=request.user)
    submissions = submissions.extra(order_by=('-time',))
    return json.dumps({
        'list': get_template('submission_list.html').render(Context(dict(
            submissions=submissions,
            user=user,
            ))),
        })

KnownTypes = ['.cpp', '.cc', '.h', '.cxx', '.hpp', '.c', '.txt', '.mkd']
def detect_type(path):
    base, ext = os.path.splitext(path)
    if ext in KnownTypes:
        return ext
    base, name = os.path.split(path)
    if name.lower() == 'makefile':
        return '.txt'
    return None

def read_content(fullpath):
    guess = ['utf-8', 'gbk']
    for enc in guess:
        try: return codecs.open(fullpath, encoding=enc).read()
        except Exception as e: 
            logger.debug(e)

@login_required
def show_submission(request, submissionID):
    # show a submission, require GRADER permission
    # accept GET only
    if request.method != 'GET': raise Http404()

    user = request.user
    try:
        if user.usertype == 'TA':
            submission = Submission.objects.get(id=submissionID)
        elif user.usertype == 'student':
            submission = Submission.objects.get(id=submissionID, user=user)
    except Submission.DoesNotExist:
        raise Http404()

    try:
        dec = submission.decompression
    except:
        # not decompressed 
        try:
            check_submission(submission)
        except UploadError as err:
            raise Http404()
        submission.retcode = 0
        submission.message = 'success'
        submission.save()
        dec = submission.decompression
    # dec: decompression
    comps = submission.compilation_set
    spec_ = submission.assignment.spec
    rows = []
    # rows = [(prob, contents), (prob, contents), ...]
    root = pjoin(dec.path, spec_.name)
    for prob in spec_.problems:
        # name, contents
        #   contents = [(type, content), (type, content), ... ]
        subroot = pjoin(root, prob.name)
        contents = []
        if prob.type == spec.Problem.CODE:
            for fname in os.listdir(subroot):
                fullpath = pjoin(subroot, fname)
                type = detect_type(fullpath)
                if type:
                    content = read_content(fullpath)
                    contents.append((type, fname, content))
            contents.sort(key=lambda (t, f, c): -len(c))
        elif prob.type == spec.Problem.TEXT:
            fullpath = subroot
            content = read_content(fullpath)
            contents.append(('.txt', prob.name, content))
        try:
            comID = comps.get(subpath=pjoin(spec_.name, prob.name), result='success').id
        except:
            comID = None
        rows.append((prob, submission.get_score(prob.name), comID, contents))
    return make_response(request, 'show_submission.html', {
        'rows': rows,
        'submission': submission,
        'ass': submission.assignment,
        'back': request.GET.get('back', settings.HOME_URL),
        })

@wrap_json
@usertype_only('TA')
def grade(request):
    # accept only POST method, AJAX
    if request.method != 'POST': raise Http404()
    form = ScoreForm(request.POST, initial = {'comment': ''})
    if form.is_valid():
        sid = form.cleaned_data['sid']
        try:
            submission = Submission.objects.get(id=sid)
            problem_name = form.cleaned_data['problem_name']
            score = submission.get_score(problem_name)
            if score is not None:
                score.delete()

            score = Score(submission=submission, 
                    problem_name=problem_name,
                    score=form.cleaned_data['score'],
                    comment=form.cleaned_data['comment'],
                    )
            score.save()
            return json.dumps({ 'code': 0, 
                'message': 'success. Give {} points to problem "{}".'.format(
                    score.score, score.problem_name)
                })
        except Exception as e:
            return json.dumps({'code': 1, 'message': unicode(e)})
    else:
        return json.dumps({'code': 2,'message': unicode(form.errors)})

@wrap_json
@usertype_only('TA')
def run_prog(request, comID):
    if request.method != 'POST': raise Http404()
    try:
        compilation = Compilation.objects.get(id=comID)
    except:
        return json.dumps({'code': 1, 
            'message': 'No such compilation. Make sure you\'ve compiled.'})
    prog = grade_.run(compilation)
    return json.dumps({'code': 0,
        'runID': str(prog.id),
        })

@wrap_json
@usertype_only('TA')
def interact_prog(request, runID):
    if request.method != 'POST': raise Http404()
    try:
        data = request.POST['input']
        prog = grade_.Run.objects.get(id=runID)
        out, err = prog.interact(data)
        return json.dumps({
            'code': 0,
            'retcode': prog.proc.poll(),
            'stdout': out,
            'stderr': err,
            })
    except Exception as e:
        logger.debug(traceback.format_exc())
        return json.dumps({
            'code': 1,
            'message': unicode(e),
            })

@wrap_json
@usertype_only('TA')
def stop_prog(request, runID):
    if request.method != 'POST': raise Http404()
    prog = grade_.Run.objects.get(id=runID)
    prog.stop()

@wrap_json
@login_required
def delete_submission(request, submissionID):
    user = request.user
    try:
        if user.usertype == 'TA':
            submission = Submission.objects.get(id=submissionID)
        else:
            submission = Submission.objects.get(id=submissionID, user=user)
        submission.delete()
        # logger.log('Delete submission #{}'.format(submission.id))
    except OSError as e:
        logger.debug('Failed to delete submission #{}\n{}'.format(submissionID, str(e)))
        return json.dumps(False)
    return json.dumps(True)

@usertype_only('TA')
def assign(request, assID):
    pass

@usertype_only('TA')
def delete_ass(request, assID):
    assignment = spec.Assignment.objects.get(id=assID)
    assignment.delete()
    return HttpResponseRedirect(settings.ASSIGNMENT_URL)

