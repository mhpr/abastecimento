from django.shortcuts import render
from abastecimento.models import Abastecimento,Posto,Veiculo
# Create your views here.
from django.core import serializers
import json
from django.http import HttpResponse
import math
from datetime import datetime, date,timedelta
from urlparse import urlparse, parse_qs
import time
from django.db import transaction
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
	"""
	home page
	"""
	# data = simplejson.dumps(some_data_to_dump)
	std = request.GET.get('std', False)
	placas = request.GET.get('placas', None)
	date_months = request.GET.get('monthsago', 12)
	date_range = request.GET.get('date_range', "01/07/2016 - 01/10/2016")
	date_str_start,date_str_end = date_range.replace(" ","").split('-')
	start_date , end_date = datetime.strptime(date_str_start, '%d/%m/%Y'),datetime.strptime(date_str_end, '%d/%m/%Y')
	if date_months:
		date_months = int(date_months)
	# data2 = serializers.serialize('json', some_data_to_dump)
	start = datetime.today()
	end = datetime.today()
	new_start = start + timedelta(days=-1*date_months * 365/12) #day can be negative
	#placas
	if placas:
		placas = placas.split(',')
		placas = Veiculo.objects.filter(placa__in=placas).values_list('placa','isVeiculo').distinct()
	else:
		placas = []
		placas = Abastecimento.objects.filter(hodometro__gt=0,criado_date__range=[start_date, end_date]).values_list('veiculo__placa','veiculo__isVeiculo').distinct()
	finalarray = []
	finalarrayPivot = []
	veiculos_litros = {}
	veiculos_diff = {}
	dates = []
	if len(placas)>0:
		dates =  map(lambda (x,):x.strftime("%Y/%m/%d"),Abastecimento.objects.filter(veiculo__placa__in=map(lambda (x,y):x,placas),criado_date__range=[start_date, end_date]).order_by('criado_date').values_list('criado_date').distinct())
		veiculos_data = {}
		veiculos_consumption = {}
		for pl,isveiculo in placas:
			veiculos_data[pl] =   Abastecimento.objects.filter(veiculo__placa=pl,criado_date__range=[start_date, end_date]).order_by('criado_date').values('hodometro','criado_date','quantidade')
			consumption = {}
			litros = {}
			diffs = {}
			consumption_datavalues = []
			anterior_value = {}
			for i,veiculo_data in enumerate(veiculos_data[pl]):
				if i== 0:
					anterior_value = veiculo_data
				else:
					consumo_value = abs(veiculo_data['hodometro']-anterior_value['hodometro'])
					consumption[veiculo_data['criado_date'].strftime("%Y/%m/%d")]=consumo_value
					consumption_datavalues.append(consumo_value)
					litros[veiculo_data['criado_date'].strftime("%Y/%m/%d")]=anterior_value['quantidade']
					diffs[veiculo_data['criado_date'].strftime("%Y/%m/%d")]=str(veiculo_data['hodometro'])+'-'+str(anterior_value['hodometro'])
					anterior_value = veiculo_data
			veiculos_consumption[pl] = consumption
			veiculos_litros[pl] = litros
			veiculos_diff[pl] = diffs
			# if std:
			# 	if len(consumption_datavalues)>1:
			# 		std_value = pstdev(consumption_datavalues)
			# 	else:
			# 		std_value = 0
			# 	with_std_value = False
			# 	if with_std_value:
			# 		consumption_data_data = [[data_criado,[dif,std_value]] for data_criado,dif,litros in consumption]
			# 	else:
			# 		consumption_data_data = [[data_criado,dif] for data_criado,dif,litros in consumption]
		for i,date_val in enumerate(dates):
			finalarray.append([date_val])
			for pl,isveiculo in placas:
				finalarray[i].append(veiculos_consumption[pl].get(date_val,None))

		for i,(pl,isveiculo) in enumerate(placas):
			finalarrayPivotElement = {}
			finalarrayPivotElement['nome'] = pl
			dataformeanhomometro = []
			dataformeanlitros = []
			for i,date_val in enumerate(dates):
				dataformeanhomometro.append(veiculos_consumption[pl].get(date_val,0))
				dataformeanlitros.append(veiculos_litros[pl].get(date_val,0))
				formatedOut = ''
				output = (veiculos_consumption[pl].get(date_val,None),veiculos_litros[pl].get(date_val,None))
				if not (None,None)== output:
					formatedOut =  (str(veiculos_consumption[pl].get(date_val,None))+('km' if isveiculo else 'Hr'),str(veiculos_litros[pl].get(date_val,None))+'litros')
				finalarrayPivotElement[date_val] = formatedOut
			finalarrayPivotElement['media'] = str(mean(dataformeanhomometro))+(' km' if isveiculo else ' Hr')
			finalarrayPivotElement['consumo'] = str(consumo(dataformeanhomometro,dataformeanlitros,isveiculo))+('km/litro' if isveiculo else 'litro/Hr')
			finalarrayPivot.append(finalarrayPivotElement)

	# print query
	consumption_data = {}
	consumption_data['data'] = finalarrayPivot
	consumption_data['dates'] = dates
	consumption_data['datapivot'] = finalarray
	consumption_data['litros'] = veiculos_litros
	consumption_data['diffs'] = veiculos_diff
	consumption_data['labels'] = map(lambda (x,y):x,placas)
	data4 =		json.dumps(consumption_data)
	return HttpResponse(data4, content_type='application/json')

@login_required
def labels_available(request):

	placas = [ i for (i,) in Abastecimento.objects.filter(hodometro__gte=0).values_list('veiculo__placa').distinct()]
	data4 =		json.dumps(placas)
	return HttpResponse(data4, content_type='application/json')



@login_required
def labels_favorites(request):
	placas = [ i for (i,) in Veiculo.objects.filter(favorito=True).values_list('placa').distinct()]
	data4 =		json.dumps(placas)
	return HttpResponse(data4, content_type='application/json')

@login_required
def update_labels_favorites(request):
	with transaction.atomic():
		placas = request.GET.get('placas', None)
		if placas:
			placas = placas.split(',')
		else:
			placas = []
		for veiculo in Veiculo.objects.all():
			if veiculo.placa in placas:
				veiculo.favorito=True
			else:
				veiculo.favorito=False
			veiculo.save()
	data4 =		json.dumps("ok")

	return HttpResponse(data4, content_type='application/json')


def consumo(data,litros,isveiculo=True):
	if len(data)<=0:
		return 0
	if isveiculo:
		return sum(data)/sum(litros,000.1)
	else:
		return sum(litros)/sum(data,000.1)

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n <= 0:
        return 0
    else:
    	return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5