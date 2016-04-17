<%namespace file="../notes/common.mako" import="note_selector"/>
<%namespace file="../tasks/common.mako" import="task_selector"/>
<div class="dl60 easyui-dialog"
    title="${title}"
    data-options="
        modal:true,
        draggable:false,
        resizable:false,
        iconCls:'fa fa-pencil-square-o'
    ">
    ${h.tags.form(
        request.url, 
        class_="_ajax %s" % ('readonly' if readonly else ''), 
        autocomplete="off",
        hidden_fields=[('csrf_token', request.session.get_csrf_token())]
    )}
        <div class="easyui-tabs h100" data-options="border:false,height:300">
            <div title="${_(u'Main')}">
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"date"), True, "date")}
                    </div>
                    <div class="ml15">
                        ${h.fields.date_field('date', item.date if item else None)}
                        ${h.common.error_container(name='date')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"account"), True, "account_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.accounts_combogrid_field(
                            request,
                            'account_id',
                            item.account_id if item else None,
                            show_toolbar=(not readonly if readonly else True),
                        )}
                        ${h.common.error_container(name='account_id')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"service"), True, "service_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.services_combogrid_field(
                            request,
                            'service_id',
                            item.service_id if item else None,
                            show_toolbar=(not readonly if readonly else True),
                        )}
                        ${h.common.error_container(name='service_id')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"vat, %"), True, "vat")}
                    </div>
                    <div class="ml15">
                        ${h.tags.text(
                            'vat', 
                            item.vat if item else None, 
                            class_="easyui-textbox w20 easyui-numberbox", 
                            data_options="min:0,precision:2,max:100"
                        )}
                        ${h.common.error_container(name='vat')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"calc method"), True, "calc_method")}
                    </div>
                    <div class="ml15">
                        ${h.fields.vats_calc_methods_combobox_field(
                            'calc_method',
                            item.calc_method.key if item else None
                        )}
                        ${h.common.error_container(name='calc_method')}
                    </div>
                </div>
                <div class="form-field mb05">
                    <div class="dl15">
                        ${h.tags.title(_(u"description"), False, "descr")}
                    </div>
                    <div class="ml15">
                        ${h.tags.text(
                            'descr', 
                            item.descr if item else None, 
                            class_="easyui-textbox w20", 
                            data_options="multiline:true,height:80"
                        )}
                        ${h.common.error_container(name='descr')}
                    </div>
                </div>
            </div>
            <div title="${_(u'Notes')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${note_selector(
                        values=([note.id for note in item.resource.notes] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
            <div title="${_(u'Tasks')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${task_selector(
                        values=([task.id for task in item.resource.tasks] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
        </div>
        <div class="form-buttons">
            <div class="dl20 status-bar"></div>
            <div class="ml20 tr button-group">
                ${h.tags.submit('save', _(u"Save"), class_="button easyui-linkbutton")}
                ${h.common.reset('cancel', _(u"Cancel"), class_="button danger easyui-linkbutton")}
            </div>
        </div>
    ${h.tags.end_form()}
</div>
