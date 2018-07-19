# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save, post_delete, pre_save

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.utils.encoding import python_2_unicode_compatible
from datetime import datetime

# class Responsavel(User):

# 	def __str__(self):              # __unicode__ on Python 2
# 		return self.username

@python_2_unicode_compatible
class Obra(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	criado_date = models.DateField("Data Criada", auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado", blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome


@python_2_unicode_compatible
class Operador(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	cpf = models.CharField(max_length=20,blank=True, null=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	class Meta:
		ordering = ['nome',]
		
	def __str__(self):
		return self.nome+' - cpf: '+(str(self.cpf) if self.cpf else 'Nao Tem')

# Create your models here.
@python_2_unicode_compatible
class Posto(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	cnpj = models.CharField(max_length=20,blank=True, null=True)
	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)
	observacao = models.TextField( blank=True, null=True)

	def __str__(self):
		return self.nome+' - cnpj: '+(str(self.cnpj) if self.cnpj else 'Nao Tem')

TIPO_VEICULOS = (
	('PROPRIO', 'Frota própria'),
	('PROPRIO-SEM', 'Próprio sem horímetro / odômetro'),
	('TERCEIRO-SEM', 'Terceirizados sem o desconto de combustível na medição'),
	('TERCEIRO-COM', 'Terceirizados com desconto do combustível na medição')
)

MAQUINA_VEICULO = (
	(False, 'Maquina'),
	(True, 'Veiculo')
)

@python_2_unicode_compatible
class Veiculo(models.Model):
	placa = models.CharField(verbose_name="Placa/Codigo Interno",max_length=30,primary_key=True)
	
	tipo = models.CharField(max_length=13, choices=TIPO_VEICULOS,blank=True, null=True)
	isVeiculo = models.BooleanField(choices=MAQUINA_VEICULO,default=True,blank=False, null=False,verbose_name="Veiculo/Maquina ")
	observacao = models.TextField( blank=True, null=True)
	favorito = models.BooleanField(verbose_name="Favorito no grafico",default=False)
	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	class Meta:
		ordering = ['placa',]
	
	def __str__(self):
		return unicode(self.placa)+' - TIPO: '+str(self.tipo)


TIPOS_COMBUSTIVEL = (
	('DS5', 'DS5'),
	('ALC', 'Alcool'),
	('DS1', 'DS1'),
	('GSA', 'Gasolina Aditivada'),
	('GSC', 'Gasolina Comum'),
	('ARLA', 'ARLA'),
	('LUB', 'LUB'),
)

def validate_hodometro_and_veiculo_type(value):
	if value <0 :
		raise ValidationError(
			_('Esse campo não pode ter valor %(value)s, o campo deve ter valor maior ou igual a zero'),
			params={'value': value},
		)


@python_2_unicode_compatible
class Abastecimento(models.Model):
	vale = models.CharField(max_length=50,verbose_name="Vale/Cupom",blank=True, null=True)
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo/Equipamento")
	motorista = models.ForeignKey(Operador,verbose_name="Motorista/Operador",related_name='+')
	posto = models.ForeignKey(Posto,verbose_name="Posto de abastecimento")
	hodometro = models.IntegerField('Hodômetro/Horimetro',default=0,validators= [validate_hodometro_and_veiculo_type])
	quantidade = models.FloatField('Quantidade em Litros')
	valor = models.FloatField('Valor Pago R$')
	combustivel = models.CharField(max_length=10, choices=TIPOS_COMBUSTIVEL)
	responsavel = models.ForeignKey(User,verbose_name="Responsável pelo abastecimento")
	obra = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)

	notafiscal = models.CharField(max_length=20,blank=True, null=True)

	criado_date = models.DateTimeField("Data Abastecimento",default=datetime.now)
	atualizado_date = models.DateTimeField("Data Abastecimento Atualizado",
			blank=True, null=True,auto_now=True)
	observacao = models.TextField( blank=True, null=True)

	def __str__(self):
		return unicode(self.id)

	# This method will be used in the admin display
	def valor_display(self):
		# Normally, you would return this:
		# return '${0:1.2f}'.format(self.budget)
		# but a decimal field will display itself correctly
		# so we can just do this:
		return 'R${0}'.format(self.valor)

	def responsavel_display(self):
		# Normally, you would return this:
		# return '${0:1.2f}'.format(self.budget)
		# but a decimal field will display itself correctly
		# so we can just do this:
		return self.responsavel.username
