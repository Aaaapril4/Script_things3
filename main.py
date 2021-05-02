import datetime as dt
import webbrowser
import configparser
import sys



def _num_distribute(begin, end, eachday, binn):
    '''
    Calculate the number in each bin
    Return:
        list of the end of each bin
    '''

    if eachday != "":
        eachday = int(eachday)
        distribution = list(range(begin-1, end, eachday))
    else:    
        total = end - begin + 1
        each = total // binn + int(bool(total % binn))
        distribution = list(range(begin-1, end, each))
    
    if end not in distribution:
        distribution.append(end)
    distribution.pop(0)

    return distribution



def _get_rest_num(i, interval, rest_index):
    total = 0
    end = i + interval + 1
    while i <= end:
        if i % 7 in rest_index:
            total = total + 1
        i = i + 1
    
    return total




def _get_date_begin_end(begindate, enddate, interval, buffer, rest):
    '''
    Calculate the work time according to the begin and end time
    Return:
        A list of work date
    '''

    interval = int(interval) if interval != '' else 0
    buffer = int(buffer) if buffer != '' else 0
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    rest_index = []
    for day in rest:
        dif = weekdays.index(day) - begindate.weekday()
        dif = dif + 7 if dif < 0 else dif
        rest_index.append(dif)
    
    work_date = []
    total = (enddate - begindate).days - buffer
    i = 0

    while i in rest_index:
        i = i + 1

    while i <= total:
        work_date.append((begindate + dt.timedelta(i)).isoformat())
        i = i + 1 + interval + _get_rest_num(i, interval, rest_index)

    return work_date



def _timesetting(para):
    setting = para["PARAMETER"].get("deadline or day")
    if setting.lower() == "deadline":
        return "deadline"
    elif setting.lower() == "day":
        return "when"



def todo_url(work_date, distribution, para):
    '''
    Generate todo from url
    Return:
        None
    '''

    string = ""
    if para["BASIC"].getboolean("create_project"):
        if para["BASIC"].get("area").lower() != 'none' and para["BASIC"].get("area") != '':
            string = "&".join((string, f'area={para["BASIC"].get("area")}'.replace(' ', '%20')))
        url = 'things:///add-project?title={}'.format(para["BASIC"].get("project").replace(' ', '%20')) + string
        webbrowser.open(url)

    string = ""
    prefix = para["NAME"].get("prefix")
    suffix = para["NAME"].get("suffix")
    projectname = para["BASIC"].get("project").replace(' ','%20')
    notes = para["PARAMETER"].get("notes").replace(' ','%20')
    timesetting = _timesetting(para)

    for i in range(len(distribution)):
        title = f'{prefix} {distribution[i]} {suffix}'.replace(' ', '%20')
        
        url = f'things:///add?title={title}&{timesetting}={work_date[i]}&list={projectname}&notes={notes}'
        webbrowser.open(url)
    
    return
    


def config(para):
    '''
    The main function
    Return:
        None
    '''

    begindate = dt.date.fromisoformat(para["CALTIME"].get("begindate"))
    enddate = dt.date.fromisoformat(para["CALTIME"].get("enddate"))
    if para["CALTIME"].get("begin-end or specific-day") == "begin-end":
        work_date = _get_date_begin_end(begindate, enddate, para["CALTIME"].get("interval"), int(para["CALTIME"].get("buffer")), para["CALTIME"].get("rest").lower().split(','))
    else:
        sys.exit("Need to define begin-end or fix-interval")
    distribution = _num_distribute(int(para["CONTENT"].get("begin")), int(para["CONTENT"].get("end")), para["CONTENT"].get("eachday"), len(work_date))
    todo_url(work_date, distribution, para)

    return


if __name__ == "__main__":
    para = configparser.ConfigParser()
    para.read("para.ini")
    config(para)