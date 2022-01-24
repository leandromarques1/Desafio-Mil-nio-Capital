import json 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta


def importar_contract(contractPath):
	with open(contractPath, encoding='utf-8') as myJSON:
		dados = json.load(myJSON)
	return dados

def converter_toDatetime(date):
	'''Converter de String para Datetime'''
	return datetime.strptime(date, '%Y-%m-%d').date()

def date_Last_DueDate(dataDigitada, contract):
	''' Analisar a data digitada pelo usuário, e comparar com as
		datas das amortizações.
		--> Retornar a data da Última Amortização
		--> Se não houver tido amortizações ainda, 
			retornar a Data de Emissão
	'''
	cont = 0
	for i in range(0,len(contract["schedules"])):
		dataEvento = contract["schedules"][i]["due_date"]
		#Se houver tido evento de Amortização antes da Data digitada
		if (converter_toDatetime(dataEvento) < converter_toDatetime(dataDigitada)):
			cont = cont + 1
		else:
			break

	if (cont == 0): #Se não existirem eventos de Amortização antes da data digitada
		last_due_date = dadosContrato["start_date"]
	else:
		last_due_date = dadosContrato["schedules"][cont - 1]["due_date"]
	
	return last_due_date

def diasUteis(data_inicio, data_fim):
	date1 = converter_toDatetime(data_inicio)
	date2 = converter_toDatetime(data_fim)

	quant_dias = (date2-date1).days
	numFDS = 0			#Nº de dias em Finais de Semana (Sábados e Domingos)
	numFeriados = 0		#Nº de Feriados Nacionais
	feriadosFDS = 0

	newDate = date1
	for i in range(1,quant_dias):
		newDate = newDate + timedelta(days=1)
		if (newDate.strftime('%A') == 'Saturday' or newDate.strftime('%A') == 'Sunday'):
			numFDS = numFDS + 1

	#Leitura do arquivo "feriados.csv"
	df = pd.read_csv("../feriados.csv")

	for i in df["Data"]:
		i = converter_toDatetime(i)
		if (i>=date1 and i<=date2):
			numFeriados = numFeriados + 1
			if(i.strftime('%A') == 'Saturday' or i.strftime('%A')=='Sunday'):
				feriadosFDS = feriadosFDS + 1

	diasUteis = quant_dias - (numFDS + numFeriados - feriadosFDS)
	return diasUteis
    
def VNA(dataDigitada, contract):
	'''Calculando o Valor Nominal Atualizado (VNA)'''
	VNE = contract["emission_price"]
	somatorioAmortizacao = 0
	for i in range (0,len(contract["schedules"])):
		dataEvento = contract["schedules"][i]["due_date"]
		percentualAmortizacao = contract["schedules"][i]["amount"]
		if (converter_toDatetime(dataEvento) < converter_toDatetime(dataDigitada)):
			A_ti = (VNE)*(percentualAmortizacao)
			somatorioAmortizacao = somatorioAmortizacao + A_ti
		else:
			break

	return VNE - somatorioAmortizacao

def PU_Par(VNA, j_emissao, d_uteis):
	'''Calculando o PU PAR'''
	fator = ((1+(j_emissao))**(d_uteis/252))
	return VNA*fator

#def PU_Oper(somatorioJ, somatorioA, j_neg, du_i, du_j):
def PU_Oper(j_neg, dataDigitada, contract):
	'''
		PU Operação --> é dado pelo somatório dos eventos remanescentes 
						que incidirão sobre a debênture avaliada
						
		somatorioJ --> ????? (não entendi - aqui é o gargalo p/ finalizar questão)
		somatorioA --> ????? (não entendi - aqui é o gargalo p/ finalizar questão) 
		j_neg --> taxa de juros indicada pelo usuário para a realização do negócio (a.a.)/
		du_i  --> nº de dias úteis entre a data de cálculo 
				  e a DATA DO EVENTO DE JUROS considerado
		du_j  --> nº de dias úteis entre a data de cálculo e a 
				  DATA DO EVENTO DE AMORTIZAÇÃO considerado
	'''
	# Parte 1: levar à valor futuro os pagamentos
	#somatorioJ = 
	#somatorioA = 

	j_emissao = contract["spread"]
	
	datasAmortizações = []
	numParcelas = len(contract["schedules"])
	for i in range(0,num_schedules,1):
		datasAmortizações.append(contract["schedules"][i]["due_date"])

	print(datasAmortizações)

	parcelas_ValorFuturo = []
	for i in range(0,num_schedules,1):
		print("\nParcela",i+1,"a Valor futuro:")
		valorAmortizacao = (contract["schedules"][i]["amount"])*(contract["emission_price"])
		print("\tValor Amortizacao:",valorAmortizacao)
		print("\tData digitada:", dataDigitada)
		print("\tData a trabalhar:",contract["schedules"][i]["due_date"])
		
		valorAtualizado = VNA(contract["schedules"][i]["due_date"], contract)
		print("\tValor Atualizado:",valorAtualizado)
		
		dataUltimoEvento = date_Last_DueDate(contract["schedules"][i]["due_date"], contract)
		d_uteis = diasUteis(dataUltimoEvento, contract["schedules"][i]["due_date"])
		
		print("\tDias uteis:",d_uteis)
		print("\tPU Par: ",PU_Par(valorAtualizado, j_emissao, d_uteis))
		
		juros_a_Pagar = PU_Par(valorAtualizado, j_emissao, d_uteis) - valorAtualizado
		print("\tJuros a Pagar: ", juros_a_Pagar)
		valorFuturo = valorAmortizacao + juros_a_Pagar
		parcelas_ValorFuturo.append(valorFuturo)

	print("\nParcelas a Valor Futuro: ", parcelas_ValorFuturo)
	'''
	for i in range(0,num_schedules,1):
		print(datasAmortizações[i])
		print("Nº de dias úteis:", diasUteis(dataDigitada,datasAmortizações[i]))
	
	somatorioJ = 0 
	jurosFuturo = 0 
	valorAtualizado = VNA(dataDigitada, contract)
	for i in range(0,num_schedules,1):
		print("\nIteração nº", i)
		if (i==0):
			du_t = diasUteis(contract["start_date"],contract["schedules"][i]["due_date"])
		else:
			du_t = diasUteis(contract["schedules"][i-1]["due_date"],contract["schedules"][i]["due_date"])
		print("du_t: ",du_t)
		jurosFuturo = valorAtualizado*(((1+j_emissao)**(du_t/252))-1)
		print("jurosFuturo: ", jurosFuturo)
		#somatorioJ = somatorioJ + jurosFuturo + (contract["schedules"][i]["amount"]*contract["emission_price"])
		somatorioJ = somatorioJ + (PU_Par(VNA, j_emissao, d_uteis) - VNA(dataDigitada, contract))
		#print("somatorioJ: ", somatorioJ)
	#print("jurosFuturo: ", jurosFuturo)

	'''

	# Parte 2: trazer o fluxo futuro à valor presente 
	#		   para a data que estamos calculando (01/01/2022) 
	#		   com a taxa informada
	'''
	P = somatorioJ/((1 + (j_neg/100))**(du_i/252))
	print("P = ",P)
	Q = somatorioA/((1 + (j_neg/100))**(du_j/252))
	print("Q = ",Q)
	#return P + Q
	print("PU Oper = ", P + Q)
	'''
	parcelas_ValorPresente = []
	for i in range (0,numParcelas,1):	
		print("\nParcela",i+1,":",parcelas_ValorFuturo[i])
		print("\tData digitada:",dataDigitada)
		dataUltimoEvento = date_Last_DueDate(contract["schedules"][i]["due_date"], contract)
		print("\tdataUltimoEvento:", dataUltimoEvento)
		d_uteis = diasUteis(dataDigitada, contract["schedules"][i]["due_date"])
		if (d_uteis>0):
			print("\tDias Uteis:",d_uteis)
			print("\tJuros Negociação:",j_neg)
			valorPresente = (parcelas_ValorFuturo[i])/((1+(j_neg/100))**(d_uteis/252))
			print("\tValor Presente:",valorPresente)
			parcelas_ValorPresente.append(valorPresente)

	print("\nParcelas a Valor Presente: ", parcelas_ValorPresente)
	print("PU Operacao:", sum(parcelas_ValorPresente))

if __name__ == '__main__':
	print("\n============== Contrato Base ==============")
	#nome_contrato = input("Digite o nome do contrato (Formato a ser escrito: '../contratoX.json'): ")
	#nome_contrato = "../contratoX.json"
	nome_contrato = "../../contratoE.json"
	dadosContrato = importar_contract(nome_contrato)

	print('\n')
	print("Identificador da operação (contract):", dadosContrato["contract"])
	print("Valor do PU de emissão da operação (emission_price):", dadosContrato["emission_price"])
	print("Data de emissão da operação (start_date):", dadosContrato["start_date"])
	print("Indexador da operação (index):", dadosContrato["index"])
	print("Taxa de juros da operação (spread):", dadosContrato["spread"])
	num_schedules = len(dadosContrato["schedules"])
	print("Quantidade de Schedules:",num_schedules)

	for i in range(0,num_schedules,1):
		print(i+1,"ª amortização")
		print("\tData de Vencimento: ", dadosContrato["schedules"][i]["due_date"])
		print("\tPercentual de amortização: ",dadosContrato["schedules"][i]["amount"])

	print("\n============== Entrar com Dados p/ Cálculo ==============")

	valorEmissao = dadosContrato["emission_price"]
	print("\nValor (PU) de emissão - Capital inicial emprestado (R$): ", valorEmissao)
	taxa_juros = dadosContrato["spread"]
	print("Spread - Taxa de juros a.a. (%): ",taxa_juros)

	# Data Digitada: digitar data de referência para o Cálculo
	#dataCalculo = input("Digitar data desejada para a análise: ")
	dataCalculo = "2022-01-01"
	#dataCalculo = "2018-03-08"
	print("Data calculo: ", dataCalculo)
	while (converter_toDatetime(dataCalculo) < converter_toDatetime(dadosContrato["start_date"])):
		print("Data digitada anterior à data de Emissão do contrato Trabalhado!")
		dataCalculo = input("Por favor, digitar novamente: ")

	# Data de emissão ou a data do último evento de pagamento de juros (o mais recente)
	dataUltimoEvento = date_Last_DueDate(dataCalculo, dadosContrato)
	print("Data Ultimo Evento de Amortização: ", dataUltimoEvento)

	# Quantidade de dias úteis entre 
	# a dataUltimoEvento e a data de cálculo
	numDiasUteis = diasUteis(dataUltimoEvento, dataCalculo)
	print("Quantidade de Dias úteis entre essas duas datas: ", numDiasUteis)

	print("\n============== VNA e PU Par ==============")
	print("Contrato escolhido: ",dadosContrato["contract"])
	print("Emission Price (VNE): ", dadosContrato["emission_price"])
	valorAtualizado = VNA(dataCalculo, dadosContrato)
	print("VNA:", valorAtualizado)
	print("PU Par:",PU_Par(valorAtualizado, taxa_juros, numDiasUteis))

	print("\n============== PU Operacao ==============")
	print("Indexador da operação: ", dadosContrato["index"])
	#jurosNegociacao = float(input("Digite taxa de juros para realização do negócio (em %): "))
	jurosNegociacao = 5.0
	#jurosNegociacao = 14.40
	print("Juros Negociação:",jurosNegociacao,"%")
	#print("PU Operacao:",PU_Oper(jurosNegociacao, dataCalculo, dadosContrato))
	PU_Oper(jurosNegociacao, dataCalculo, dadosContrato)
	#print("PU Operacao:",PU_Oper(600, 550, jurosNegociacao, 252, 504))
	#PU_Oper(600, 550, jurosNegociacao, 252, 504)	

	''''''