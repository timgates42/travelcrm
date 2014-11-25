<%inherit file="travelcrm:templates/_report.mak"/>
<h1>${_(u'Report')}: ${title}</h1>
<table width="100%">
	<tr>
		<th width="5%" align="left">#</th>
		<th width="35%" align="left">${_(u'Name')}</th>
		<th width="15%" align="right">${_(u'Income')}</th>
		<th width="15%" align="right">${_(u'Outgoing')}</th>
		<th width="15%" align="right">${_(u'Balance')}</th>
		<th width="15%" align="center">${_(u'Currency')}</th>
	</tr>
	% for i, row in enumerate(rows):
	<tr>
		<td align="left">${i+1}</td>
		<td align="left">${row.get('name')}</td>
		<td align="right">${row.get('sum_to')}</td>
		<td align="right">${row.get('sum_from')}</td>
		<td align="right">
			% if row.get('balance') < 0:
				<span class="lipstic">${row.get('balance')}</span>
			% else:
				<span class="b">${row.get('balance')}</span>
			% endif
		</td>
		<td align="center">${row.get('currency')}</td>
	</tr>
	% endfor
</table>
