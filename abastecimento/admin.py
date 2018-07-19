#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from import_export import resources
from django.contrib.auth.admin import UserAdmin

from import_export.admin import ImportExportMixin, ImportExportModelAdmin
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField

# Register your models here.
from django.db import transaction
from abastecimento.models import Abastecimento,Posto,Veiculo,Operador,Obra,TIPO_VEICULOS
from django import forms
from django.utils.translation import ugettext_lazy as _
from daterange_filter.filter import DateRangeFilter

# class ResponsavelAdmin(UserAdmin):

# 	search_fields = ['username']
# admin.site.register(Responsavel, ResponsavelAdmin)

admin.site.site_title = 'Ancar Modulo Administrativo'
admin.site.site_header = 'Ancar Admin'

class AbastecimentoResource(resources.ModelResource):
	def __str__(self):
		return ""
	class Meta:
		model = Abastecimento
		def __str__(self):
			return self.model.notafiscal

	def before_save_instance(self,instance,using_transactions,dry_run):
		print instance
		pass

	def before_import_row(self,row, **kwargs):
		with transaction.atomic():
			try:
				val = float(row['hodometro'])
			except Exception as err:
				row['hodometro'] = 0

			try:
				val = float(row['quantidade'])
			except Exception as err:
				row['quantidade'] = 0

			try:
				val = float(row['valor'])
			except Exception as err:
				row['valor'] = 0
			print row
			row['id'] = unicode(row['id'])
			vale = row['vale']

			placa = unicode(row['veiculo']).strip() 
			obj, created = Veiculo.objects.update_or_create(placa=placa)

			nome = unicode(row['posto']).strip()
			obj, created  = Posto.objects.update_or_create(nome=nome)

			nome = unicode(row['motorista']).strip()
			obj, created = Operador.objects.update_or_create(nome=nome)

			nome = row['responsavel']
			permissions = []
			permissions.append(Permission.objects.get(name='Can delete abastecimento'))
			permissions.append(Permission.objects.get(name='Can change abastecimento'))
			permissions.append(Permission.objects.get(name='Can add abastecimento'))
			permissions.append(Permission.objects.get(name='Can delete operador'))
			permissions.append(Permission.objects.get(name='Can change operador'))
			permissions.append(Permission.objects.get(name='Can add operador'))
			permissions.append(Permission.objects.get(name='Can delete veiculo'))
			permissions.append(Permission.objects.get(name='Can change veiculo'))
			permissions.append(Permission.objects.get(name='Can add veiculo'))
			permissions.append(Permission.objects.get(name='Can delete posto'))
			permissions.append(Permission.objects.get(name='Can change posto'))
			permissions.append(Permission.objects.get(name='Can add posto'))

			permissions.append(Permission.objects.get(name='Can delete obra'))
			permissions.append(Permission.objects.get(name='Can change obra'))
			permissions.append(Permission.objects.get(name='Can add obra'))
			# listobj = Responsavel.objects.filter(username=nome)
			# obj,created = Responsavel.objects.update_or_create(username=nome,is_staff=True) 
			# obj.user_permissions.set(permissions)
			# obj.set_password('usuario123')

			obj,created = User.objects.update_or_create(username=nome,password='usuario123',is_staff=True) 
			obj.user_permissions.set(permissions)
			row['responsavel'] = obj.id

		# return self.fields['name'].clean(row) == ''


class OperadorAdmin(admin.ModelAdmin):

	search_fields = ['nome', 'cpf']


admin.site.register(Operador, OperadorAdmin)

class ObraAdmin(admin.ModelAdmin):
	pass


admin.site.register(Obra, ObraAdmin)


class Abastecimentoform(forms.ModelForm):
	class Meta:
		model = Abastecimento
		fields = '__all__'

	def clean(self):
		cleaned_data = self.cleaned_data

		veiculo = self.cleaned_data.get('veiculo',None)
		hodometro = self.cleaned_data.get('hodometro',None)
		if veiculo is not None and hodometro is not None and veiculo.tipo == TIPO_VEICULOS[0][0] and hodometro<=0:
			msg = _('Valor %s Invalido de Hodometro/Horimetro   para veiculos do tipo %s'%(hodometro,veiculo.tipo))
			self._errors["hodometro"] = self.error_class([msg])
			del cleaned_data["hodometro"]
			# raise forms.ValidationError(
			# 			_('Valor %(value)s Invalido de Hodometro/Horimetro   para veiculos do tipo %(tipo)s'),
			# 			params={'value': hodometro,'tipo':veiculo.tipo},
			# 		)
		return cleaned_data


class AbastecimentoAdmin(ImportExportMixin, admin.ModelAdmin):
	resource_class = AbastecimentoResource
	
	form = Abastecimentoform
	list_display = ('id','notafiscal','vale','criado_date','hodometro','quantidade','valor_display', 'responsavel_display','veiculo')
	search_fields = ['notafiscal', 'veiculo__placa','responsavel__username','posto__nome','observacao']
	list_filter = (('criado_date',DateRangeFilter),'posto','veiculo')
	list_editable = ('notafiscal',)
	# readonly_fields=('vale','motorista','responsavel','veiculo','posto')
	
	class Media:
 		js = (
 			'js/abastecimentoAdmin.js',
 			);
 		css = {
	      'all': ('/static/css/new_abastecimento.css',) 
	    }

	def __init__(self, *args, **kwargs):
		super(AbastecimentoAdmin, self).__init__(*args, **kwargs)


	def save_model(self, request, obj, form, change):
		if not request.user.is_superuser:
			if obj.id is None:
				obj.responsavel = request.user
			obj.notafiscal =  obj.notafiscal

		obj.save()

	# def get_fields(self,request,obj=None):
	# 	if request.user.is_superuser:
	# 		return self.readonly_fields
	# 	else:	
	# 		if obj and not obj.responsavel==resquest.user: # editing an existing object
	# 			return self.readonly_fields+list_display
	# 		return self.readonly_fields

	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return self.readonly_fields
		else:	
			if obj and not obj.responsavel==request.user: # editing an existing object
				return self.readonly_fields+tuple(obj._meta.get_all_field_names())
			return self.readonly_fields+('responsavel','notafiscal')


	# def get_search_results(self, request,queryset,search_term):
	# 	print 'lkkkkkkkkkk',request.user.is_superuser
	# 	if request.user.is_superuser:
	# 		return Abastecimento.objects.all()
	# 	else:
	# 		return Abastecimento.objects.filter(responsavel=request.user)

admin.site.register(Abastecimento, AbastecimentoAdmin)

class PostoAdmin(admin.ModelAdmin):

    search_fields = ['nome', 'cnpj','observacao']
    list_filter = ('criado_date','atualizado_date')


admin.site.register(Posto, PostoAdmin)

class Veiculoform(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(Veiculoform, self).__init__(*args, **kwargs)
		self.fields['isVeiculo'].choices = self.fields['isVeiculo'].choices[1:]

	class Meta:
		model = Veiculo
		fields = '__all__'

		def clean(self):
			start_date = self.cleaned_data.get('veiculo')
			if start_date > end_date:
				raise forms.ValidationError("Dates are fucked up")
			return self.cleaned_data

class VeiculoAdmin(admin.ModelAdmin):

	form = Veiculoform
	search_fields = ['placa','tipo','observacao']
	list_filter = ('criado_date','atualizado_date','tipo')
	radio_fields = {"isVeiculo": admin.VERTICAL}


admin.site.register(Veiculo, VeiculoAdmin)

