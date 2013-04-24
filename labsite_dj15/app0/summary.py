from account import User
from spec import Assignment
from upload import Submission

def summary():
    asss = Assignment.objects.all()
    students = User.objects.filter(usertype='student').extra(order_by=['studentID'])
    heads = ['studentID']
    heads.extend(ass.title for ass in asss)
    data = []
    for user in students:
        row = [user.studentID]
        for ass in asss:
            subm = get_last_submission(user, ass)
            row.append(subm)
        data.append(row)
    return heads, data

def get_last_submission(user, ass):
    subms = user.submissions.filter(assignment=ass, retcode=0).extra(order_by=['-time'])
    try:
        return subms[0]
    except:
        return None
