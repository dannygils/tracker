from math import ceil, floor
from itertools import permutations
import os
from turtle import onclick
import yaml
import re
import dominate
from dominate.tags import *
from dominate.util import raw
from more_itertools import peekable


doc = dominate.document(title="Roundtable Tracker")
doc.set_attribute('lang', 'en')

def to_snake_case(name):
    name = "".join(name.split())
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()

dropdowns = []
pages = []
item_links = []
with open('pages.yaml', 'r', encoding='utf-8') as pages_yaml:
    yml = yaml.safe_load(pages_yaml)
    item_links = yml['item_links']
    for dropdown in yml['dropdowns']:
        dropdown_ids = []
        for page in dropdown['pages']:
            with open(os.path.join('data', page), 'r', encoding='utf-8') as data:
                yml = yaml.safe_load(data)
                pages.append(yml)
                dropdown_ids.append((yml['title'], yml['id']))
        dropdowns.append((dropdown['name'], dropdown_ids))

page_ids = set()
section_ids = set()
for page in pages:
    if page['id'] in page_ids:
        print("Duplicate page id '" + page['id'] + "' found. All page ids must be unique.")
        quit(1)
    else:
        page_ids.add(page['id'])

    section_nums = set()
    for section in page['sections']:
        if section['id'] in section_ids:
            print("Duplicate section id '" + section['id'] + "' found in page '" + page['id'] + "'. All section ids must be unique.")
            quit(1)
        else:
            section_ids.add(section['id'])
        if section['num'] in section_nums:
            print("Duplicate section num '" + str(section['num']) + "' found in page '" + page['id'] + "'. All section nums must be unique.")
            quit(1)
        else:
            section_nums.add(section['num'])
        item_nums = set()
        items = peekable(section['items'])
        for item in items:
            if not isinstance(item, list):
                continue
            if item[0] in item_nums:
                print("Duplicate item num '" + str(item[0]) + "' in section '" + section['id'] + "' found in page '" + page['id'] + "'. All item nums must be unique within it's section.")
                quit(1)
            else:
                item_nums.add(item[0])
            if isinstance(items.peek([0])[0], list):
                sub_item_nums = set()
                item = next(items)
                for subitem in item:
                    if subitem[0] in sub_item_nums:
                        print("Duplicate sub-item num '" + str(subitem[0]) + "' in section '" + section['id'] + "' found in page '" + page['id'] + "'. All item nums must be unique within it's section.")
                        quit(1)
                    else:
                        sub_item_nums.add(subitem[0])



with doc.head:
    meta(charset="UTF-8")
    meta(name="viewport", content="width=device-width, initial-scale=1.0")
    link(rel="shortcut icon", type="image/x-icon", href="img/favicon.ico?")
    link(rel="apple-touch-icon-precomposed", href="img/favicon-152.png")
    link(rel="mask-icon", href="img/pinned-tab-icon.svg", color="#000000")
    meta(name="description", content="Cheat sheet for Elden Ring. Checklist of things to do, items to get etc.")
    meta(name="author", content="Ben Lambeth")
    meta(name="mobile-web-app-capable", content="yes")
    link(href="css/bootstrap.min.css", rel="stylesheet", id="bootstrap")
    link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css")
    link(href="css/main.css", rel="stylesheet")

with doc:
    with nav(cls="navbar navbar-expand-sm bg-dark navbar-dark"):
        with div(cls="container-fluid"):
            with div(cls="navbar-header"):
                with button(type="button", cls="navbar-toggler", data_bs_toggle="collapse", data_bs_target="#nav-collapse", aria_expanded="false", aria_controls="nav-collapse", aria_label="Toggle navigation"):
                    span(cls="navbar-toggler-icon")
            with div(cls="collapse navbar-collapse", id="nav-collapse"):
                with ul(cls="nav navbar-nav mr-auto"):
                    with li(cls="nav-item"):
                        a(href="#tabMain", data_bs_toggle="tab", cls="nav-link hide-buttons").add(i(cls="bi bi-house-fill"))
                    for name, l in dropdowns:
                        with li(cls="dropdown nav-item"):
                            a(name, cls="nav-link dropdown-toggle", href="#", data_bs_toggle="dropdown", aria_haspopup="true", aria_expanded="false").add(span(cls="caret"))
                            with ul(cls="dropdown-menu"):
                                for guide in l:
                                    li().add(a(guide[0], cls="dropdown-item show-buttons", href="#tab" + guide[1], data_bs_toggle="tab", data_bs_target="#tab" + guide[1]))
                                    # li().add(a(guide[0], cls="dropdown-item", href="#tab" + guide[1], data_bs_toggle="tab", data_bs_target="#tab" + guide[1]))
                    with li(cls="nav-item"):
                        a(href="#tabOptions", data_bs_toggle="tab", cls="nav-link hide-buttons").add(i(cls="bi bi-gear-fill"), " Options")
    with div(cls="container"):
        with div(cls="row"):
            with div(cls="col-md-12 text-center"):
                h1("Roundtable Tracker", cls="mt-3")
                text = p(cls="lead")
                text += "Contribute to the guide at the "
                text += a("Github Page", href="https://github.com/Roundtable-Hold/tracker")
        with div(cls="tab-content gap-2"):
            # Hide completed toggle
            with div(id="btnHideCompleted", cls="fade mb-3"):
                with div(cls="form-check form-switch"):
                    input_(cls="form-check-input", type="checkbox", id='toggleHideCompleted')
                    label("Hide Completed", cls="form-check-label", _for='toggleHideCompleted')
            for page in pages:
                with div(cls="tab-pane fade", id="tab" + page['id'], role="tabpanel"):
                    # Filter buttons
                    h = h2()
                    h += page['title']
                    h += span(id=page['id'] + "_overall_total")

                    with nav(cls="text-muted toc"):
                        with strong(cls="d-block h5").add(a(data_bs_toggle="collapse", role="button", href="#toc_" + page['id'], cls="toc-button")):
                            i(cls='bi bi-plus-lg')
                            raw('Table Of Contents')
                        with ul(id="toc_" + page['id'], cls="toc_page collapse"):
                            for section in page['sections']:
                                with li():
                                    a(section['title'], href="#" + section['id'])
                                    span(id=page['id']  + "_nav_totals_" + str(section['num']))

                    with div(cls="input-group"):
                        input_(type="search", id=page['id'] + "_search", cls="form-control my-3", placeholder="Start typing to filter results...")

                    with div(id=page['id']+"_list"):
                        for section in page['sections']:
                            with h4(id=section['id'], cls="mt-1"):
                                with a(href="#" + section['id'] + "_col", data_bs_toggle="collapse", data_bs_target="#" + section['id'] + "_col", cls="btn btn-primary btn-sm me-2 collapse-button", role="button"):
                                    i(cls='bi bi-chevron-up')
                                if 'link' in section:
                                    a(section['title'], href=section['link'])
                                else:
                                    span(section['title'])
                                span(id=page['id'] + "_totals_" + str(section['num']), cls="mt-0 badge rounded-pill")
                            if 'table' in section:
                                with div(id=section['id'] + "_col", cls="collapse show row", aria_expanded="true"):
                                    if isinstance(section['table'], list):
                                        table_cols = len(section['table'])
                                        size = floor(12 / table_cols)
                                    else:
                                        table_cols = section['table']
                                        size = floor(12 / table_cols)
                                    items = peekable(section['items'])
                                    if not isinstance(items.peek(), list):
                                        item = next(items)
                                        h5(item)
                                    with ul(cls='list-group list-group-flush'):
                                        if isinstance(section['table'], list):
                                            with li(cls="list-group-item d-md-block d-none").add(div(cls="row form-check")):
                                                with div(cls="col-auto"):
                                                    input_(cls="form-check-input invisible", type='checkbox')
                                                with div(cls="col").add(div(cls="row")):
                                                    for idx, header in enumerate(section['table']):
                                                        if 'table_widths' in page:
                                                            col_size = str(page['table_widths'][idx])
                                                        else:
                                                            col_size = str(size)
                                                        div(cls="col-md-" + col_size).add(strong(header))
                                        for item in items:
                                            id = str(item[0])
                                            with li(cls="list-group-item", data_id=page['id'] + '_' + str(section['num']) + '_' + id):
                                                if not isinstance(item, list):
                                                    h5(item)
                                                    continue
                                                with div(cls="row form-check checkbox"):
                                                    with div(cls="col-auto"):
                                                        input_(cls="form-check-input", type="checkbox", value="",
                                                                id=page['id'] + '_' + str(section['num']) + '_' + id)
                                                    with div(cls="col").add(div(cls="row")):
                                                        for pos in range(1, 1+table_cols):
                                                            if 'table_widths' in page:
                                                                col_size = str(page['table_widths'][pos-1])
                                                            else:
                                                                col_size = str(size)
                                                            with div(cls="col-md-" + col_size + (' col-xs-12' if item[pos] else ' d-md-block d-none')):
                                                                with label(cls="form-check-label item_content ms-0 ps-0", _for=page['id'] + '_' + str(section['num']) + '_' + id):
                                                                    if isinstance(section['table'], list) and item[pos]:
                                                                        strong(section['table'][pos-1] + ': ', cls="d-md-none d-inline-block me-1")
                                                                    if item[pos]:
                                                                        raw(item[pos])
                            else:
                                with div(id=section['id'] + "_col", cls="collapse show", aria_expanded="true"):
                                    items = peekable(section['items'])
                                    if not isinstance(items.peek(), list):
                                        item = next(items)
                                        h5(item)
                                    u = ul(cls="list-group-flush")
                                    for item in items:
                                        if not isinstance(item, list):
                                            h5(item)
                                            u = ul(cls="list-group-flush")
                                            continue
                                        id = str(item[0])
                                        with u.add(li(data_id=page['id'] + "_" + str(section['num']) + "_" + id, cls="list-group-item")):
                                            with div(cls="form-check checkbox"):
                                                input_(cls="form-check-input", type="checkbox", value="", id=page['id'] + '_' + str(section['num']) + '_' + id)
                                                label(cls="form-check-label item_content", _for=page['id'] + '_' + str(section['num']) + '_' + id).add(raw(item[1]))
                                        if isinstance(items.peek([0])[0], list):
                                            item = next(items)
                                            with u.add(ul(cls="list-group-flush")):
                                                for subitem in item:
                                                    with li(data_id=page['id'] + "_" + str(section['num']) + "_" + id + "_" + str(subitem[0]), cls="list-group-item"):
                                                        with div(cls="form-check checkbox"):
                                                            input_(cls="form-check-input", type="checkbox", value="", id=page['id'] + '_' + str(section['num']) + '_' + id + '_' + str(subitem[0]))
                                                            label(cls="form-check-label item_content", _for=page['id'] + '_' + str(section['num']) + '_' + id + '_' + str(subitem[0])).add(raw(subitem[1]))
            with div(cls="tab-pane fade", id="tabMain"):
                raw(
"""
<h3>Welcome to the Roundtable Tracker</h3>
<p>The comprehensive tracker for Elden Ring, made by completionists, for completionists.</p>
<p>This site is still a work in-progress. We are working on it every day.</p>

<h3>I have feedback, how can I contribute?</h3>
<p>Contributing is easy! And does not require you to know how to code. You can find instructions on the <a href="https://github.com/Roundtable-Hold/tracker">GitHub repository</a>. You can also simply <a href="https://github.com/Roundtable-Hold/tracker/issues">report issues</a> and we'll fix them.</p>
<p>Or you can join the <a href="https://discord.gg/pkg6ZTXR">development discord</a>, and ask us there.</p>

<h3>Can I use this for multiple characters?</h3>
<p>Yup, use the profile selector and buttons in the options tab at the top of the page to setup multiple profiles.</p>

<h3>How does the checklist status get saved?</h3>
<p>The checklist is saved to your browser's local storage. Be careful when clearing your browser's cache as it will also destroy your saved progress.</p>

<h3>Thanks</h3>
<p>This sheet would not be possible without the incredible work already done by the team at Fextralife, the team behind MapGenie, fellow redditors /u/Athrek and /u/AcceptablePackMule, and the rest of the community.</p>
<p>The foundation of this website was based on <a href="https://github.com/ZKjellberg">ZKjellberg</a>'s <a href="https://github.com/ZKjellberg/dark-souls-3-cheat-sheet">Dark Soul's 3 Cheat Sheet</a> source code.</p>

<h3>DISCLAIMER</h3>
<p>This tracker is still a work in progress, and as such, we apologize for any issues that might come about as we update the checklist and iron out bugs.</p>
<p>We will do our best to ensure that such issues remain few and far between.</p>
""")
            with div(cls="tab-pane fade gap-3", id="tabOptions"):
                h2("Options")
                with div(cls="row"):
                    div(cls="col col-12 col-md-6").add(h4("Theme selection:"))
                    div(cls="col col-12 col-md-6").add(select(cls="form-select", id="themes"))
                with div(cls="row"):
                    div(cls="col col-12 col-md-4").add(h4("Profile management:"))
                    with form(cls="form-inline input-group pull-right gap-1"):
                        with div(cls="col col-12 col-md-4"):
                            select(cls="form-select", id="profiles")
                        with div(cls="col col-12 col-md-4"):
                            with div(cls="btn-group"):
                                button("Add", cls="btn btn-primary", type="button", id="profileAdd")
                            with div(cls="btn-group"):
                                button("Edit", cls="btn btn-primary", type="button", id="profileEdit")
                            with div(cls="btn-group"):
                                button("NG+", cls="btn btn-primary", type="button", id="profileNG+")
                with div(cls="row"):
                    div(cls="col col-12 col-md-4").add(h4("Data import/export:"))
                    with div(cls="col col-12 col-md-8"):
                        with form(cls="form-inline gap-1 m-1"):
                            with div(cls="btn-group pull-left"):
                                button("Import file", cls="btn btn-primary", type="button", id="profileImport")
                            with div(cls="btn-group pull-left"):
                                button("Export file", cls="btn btn-primary", type="button", id="profileExport")
                            with div(cls="btn-group pull-right"):
                                button("Import textbox", cls="btn btn-primary", type="button", id="profileImportText")
                            with div(cls="btn-group pull-right mt-1 mt-md-0"):
                                button("Export clipboard", cls="btn btn-primary", type="button", id="profileExportText")
                    with div(cls="col col-12"):
                        textarea(id="profileText", cls="form-control")
            with div(id="profileModal", cls="modal fade", tabindex="-1", role="dialog"):
                with div(cls="modal-dialog", role="document"):
                    with div(cls="modal-content"):
                        with div(cls="modal-header"):
                            h3("Profile", id="profileModalTitle", cls="modal-title")
                            button(type="button", cls="btn-close", data_bs_dismiss="modal", aria_label="Close")
                        with div(cls="modal-body"):
                            with form(cls="form-horizontal"):
                                with div(cls="control-group"):
                                    label("Name", cls="control-label", _for="profileModalName")
                                    div(cls="controls").add(input_(type="text", cls="form-control", id="profileModalName", placeholder="Enter Profile name"))
                        with div(cls="modal-footer"):
                            button("Close", id="profileModalClose", cls="btn btn-secondary", data_bs_dismiss="modal")
                            a("Add", href="#", id="profileModalAdd", cls="btn btn-primary", data_bs_dismiss="modal")
                            a("Update", href="#", id="profileModalUpdate", cls="btn btn-primary")
                            a("Delete", href="#", id="profileModalDelete", cls="btn btn-primary")
            with div(id="NG+Modal", cls="modal fade", tabindex="-1", role="dialog"):
                with div(cls="modal-dialog", role="document"):
                    with div(cls="modal-content"):
                        with div(cls="modal-header"):
                            h3("Begin next journey?", id="profileModalTitle", cls="modal-title")
                            button(type="button", cls="btn-close", data_bs_dismiss="modal", aria_label="Close")
                        div('If you begin the next journey, all progress on the "Playthrough" and "Misc" tabs of this profile will be reset, while achievement and collection checklists will be kept.', cls="modal-body")
                        with div(cls="modal-footer"):
                            a("No", href="#", cls="btn btn-primary", data_bs_dismiss="modal")
                            a("Yes", href="#", cls="btn btn-danger", id="NG+ModalYes")

    div(cls="hiddenfile").add(input_(name="upload", type="file", id="fileInput"))

    a(cls="btn btn-primary btn-sm fadingbutton back-to-top").add(raw("Back to Top&thinsp;"), span(cls="bi bi-arrow-up"))

    script(src="js/jquery.min.js")
    script(src="js/jstorage.min.js")
    script(src="js/bootstrap.bundle.min.js")
    script(src="js/jets.min.js")
    script(src="js/jquery.highlight.js")
    script(src="js/main.js")
    script(src="js/search.js")
    script(src="js/item_links.js")
    raw("""
    <!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-B7FMWDCTF5"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'G-B7FMWDCTF5');
</script>
""")

with open('index.html', 'w', encoding='UTF-8') as index:
    index.write(doc.render())

with open(os.path.join('js', 'search.js'), 'w', encoding='UTF-8') as jsfile:
    jsfile.writelines([
        '(function($) {\n',
        "  'use strict';\n",
        '  $(function() {\n',
        '  var jets = [new Jets({\n'
        ])
    for i, page in enumerate(pages):
        jsfile.writelines([
            '    searchTag: "#' + page['id'] + '_search",\n',
            '    contentTag: "#' + page['id'] + '_list ul"\n',
            '  }), new Jets({\n' if i < len(pages) - 1 else '})];\n'
        ])
    for i, page in enumerate(pages):
        jsfile.writelines([
            '  $("#' + page['id'] + '_search").keyup(function() {\n',
            '    $("#' + page['id'] + '_list").unhighlight();\n',
            '    $("#' + page['id'] + '_list").highlight($(this).val());\n',
            '  });\n'
        ])
    jsfile.write('});\n')
    jsfile.write('})( jQuery );\n')

with open(os.path.join('js', 'item_links.js'), 'w', encoding='UTF-8') as links_f:
    links_f.writelines([
        '(function($) {\n',
        "  'use strict';\n",
        '  $(function() {\n',
    ])
    for link in item_links:
        links_f.write('    $("#' + link[0] + '").click(function () {\n')
        links_f.write('      var checked = $(this).prop("checked");\n')
        for target in link[1:]:
            links_f.write('      $("#' + target + '").prop("checked", checked);\n')
            links_f.write('      window.onCheckbox("#' + target + '");\n')
        links_f.write('    });\n')
    links_f.write('  });\n')
    links_f.write('})( jQuery );\n')