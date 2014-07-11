import json  # json support

assert auth.is_logged_in()  # all actions require login


def schedule():
    Task.get(request.vars.name).schedule()

def delete_results():
    return Task.get(request.vars.name).delete_results()

def export_excel():
    import xlwt  # Excel export support
    import io  # for files in memory

    name = request.vars.name
    task = Task.get(name)
    data = task.get_results(as_table=True)
    w = xlwt.Workbook()
    ws = w.add_sheet("data")

    ## write ##
    for x, row in enumerate(data):
        for y, cell in enumerate(row):
            ws.write(x, y, cell)

    ## save ##
    f = io.BytesIO('%s.xls' % name)
    w.save(f)
    f.seek(0)
    response.headers["Content-Type"] = "application/vnd.ms-excel"
    return f.read()

def delete_task():
    Task.get(request.vars.name).delete()

def get_task_status():
    return json.dumps({"status": Task.get(request.vars.name).status})

def new_task():
    task_name = request.vars.name
    assert not Task.get(task_name)  # Disallow overwriting of existing tasks
    Task(name=task_name).put()
    redirect("/webscraper/default/task?name=%s" % task_name)

def save_task():
    """ Takes the post request from the task form and saves the values to the task """
    task = Task.get(request.vars.task_name)
    task.period = int(request.vars.period)
    task.url_selectors = [UrlSelector(
                            url_raw=request.vars.getlist("url_raw[]")[i],
                            results_key=ndb.Key(Task, request.vars.getlist("url_results_id[]")[i]),
                            results_property=request.vars.getlist("url_results_property[]")[i],
                            start_parameter=request.vars.getlist("url_start_parameter[]")[i]
                          ) for i in range(len(request.vars.getlist("url_raw[]")))]
    task.selectors = [Selector(
                            is_key=request.vars.getlist("selector_is_key[]")[i] == "on",
                            name=request.vars.getlist("selector_name[]")[i],
                            xpath=request.vars.getlist("selector_xpath[]")[i],
                            type=Selector.TYPES[int(request.vars.getlist("selector_type[]")[i])],
                            regex=request.vars.getlist("selector_regex[]")[i],
                          ) for i in range(len(request.vars.getlist("selector_is_key[]")))]
    task.put()
    redirect("/webscraper/default/task?name=%s" % task.name)

def get_task_selector_names():
    return json.dumps([selector.name for selector in Task.get(request.vars.name).selectors])