# -*- coding: utf-8 -*-
__author__ = 'Sebastian Hofstetter'

import json  # json support
import traceback

assert auth.is_logged_in()  # all actions require login


def test_task():
    try:
        results = Task.get(request.vars.name).test()[:30]
        return json.dumps(
            {"results": "<br>".join([repr(result._to_dict(exclude=["task_key"])) for result in results])    })
    except Exception as e:
        traceback.print_exc()
        return json.dumps({"results": e.message})

def schedule_task():
    try:
        Task.get(request.vars.name).schedule()
        return json.dumps({})
    except Exception as e:
        traceback.print_exc()
        return json.dumps({"results": e.message})

def delete_results():
    return Task.get(request.vars.name).delete_results()

def export_excel():
    name = request.vars.name
    task = Task.get(name)
    response.headers["Content-Type"] = "application/vnd.ms-excel"
    return task.export_to_excel()

def export_gcs():
    name = request.vars.name
    task = Task.get(name)
    redirect(task.export_to_gcs())

def get_data():
    name = request.vars.name
    task = Task.get(name)
    query_options = Query_Options()

    if request.vars.limit:
        query_options.limit = int(request.vars.limit)
    if request.vars.cursor:
        query_options.cursor = ndb.Cursor(urlsafe=request.vars.cursor)
    elif request.vars.offset:
        query_options.offset = int(request.vars.offset)

    results = task.get_results_as_table(query_options=query_options)
    # results = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % value for value in row) for row in results)
    results = "\n".join("\t".join("%s" % value for value in row) for row in results) + "\n"
    return json.dumps(dict(results=results, cursor=query_options.cursor.urlsafe() if query_options.cursor else "", has_next=query_options.has_next))

def get_gcs_data():
    name = request.vars.name
    task = Task.get(name)
    redirect(task.get_gcs_link())

def export_task():
    name = request.vars.name
    task = Task.get(name)
    response.headers["Content-Type"] = "text/plain"
    return task.export()

def delete_task():
    Task.get(request.vars.name).delete()

def new_task():
    task_name = request.vars.name
    assert not Task.get(task_name)  # Disallow overwriting of existing tasks
    Task(name=task_name).put()
    redirect("/webscraper/default/task?name=%s" % task_name)

def save_task():
    """ Takes the post request from the task form and saves the values to the task """
    task = Task.get(request.vars.task_name)
    task.url_selectors = [UrlSelector(
                            url_raw=request.vars.getlist("url_raw[]")[i],
                            task_key=ndb.Key(Task, request.vars.getlist("url_results_id[]")[i]),
                            selector_name=request.vars.getlist("url_selector_names1[]")[i],
                            selector_name2=request.vars.getlist("url_selector_names2[]")[i],
                          ) for i in range(len(request.vars.getlist("url_raw[]")))]
    task.selectors = [Selector(
                            is_key= unicode(i) in request.vars.selector_is_key,
                            name=request.vars.getlist("selector_name[]")[i],
                            xpath=request.vars.getlist("selector_xpath[]")[i],
                            type=Selector.TYPES[int(request.vars.getlist("selector_type[]")[i])],
                            regex=request.vars.getlist("selector_regex[]")[i],
                          ) for i in range(len(request.vars.getlist("selector_name[]")))]
    task.put()

def get_task_selector_names():
    return json.dumps([selector.name for selector in Task.get(request.vars.name).selectors])

def result_count():
    i = 0
    for key in Result.query().fetch(keys_only=True):
        i += 1
    return i

def put_tasks():
    ndb.put_multi(Task.example_tasks())
    redirect("/")

def run_command():
    try:
        return json.dumps({"results": repr(eval(request.vars.command))})
    except Exception as e:
        traceback.print_exc()
        return json.dumps({"results": e.message})

def export_all_tasks():
    response.headers["Content-Type"] = "text/plain"
    return ",\n".join([task.export() for task in Task.query().fetch()])

session.forget()