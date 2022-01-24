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

def amortizacoes__a_pagar(dataDigitada, contract):
	return VNA(dataDigitada, contract)

def PU_Par(VNA, j_emissao, d_uteis):
	'''Calculando o PU PAR'''
	fator = ((1+(j_emissao))**(d_uteis/252))
	return VNA*fator

def PU_Oper(somatorioJ, somatorioA, j_neg, du_i, du_j):
	P = somatorioJ/((1 + (j_neg/100))**(du_i/252))
	Q = somatorioA/((1 + (j_neg/100))**(du_j/252))
	return P + Q

def dataVencimentoDefinitivo(contract):
	numSchedules = len(contract["schedules"])

	return contract["schedules"][numSchedules-1]["due_date"]

def plotarGrafico(contract):
	
	dataComeco = input("Digitar data de Começo da análise: ")
	dataFim = input("Digitar data de Fim da análise: ")
	
	while (converter_toDatetime(dataFim) < converter_toDatetime(dataComeco)):
		print("Data do Fim é anterior à Data do Começo !")
		dataFim = input("Por favor, digitar nova data de Fim: ")

	vencimentoContrato = dataVencimentoDefinitivo(contract)
	while (converter_toDatetime(dataFim) > converter_toDatetime(vencimentoContrato)):
		print("Data do Fim é além do Prazo de Vencimento do Contrato (",vencimentoContrato,")")
		dataFim = input("Por favor, digitar nova data de Fim: ")

	d_uteis = diasUteis(dataComeco, dataFim)
	print("Quantidade de dias uteis entre datas digitadas:", d_uteis)

	j_emissao = contract["spread"]
	
	# EIXO X --> nº de dias 
	# EIXO Y --> preço de PU PAR (em relação ao dia)
	
	x = np.arange(0, d_uteis, 1)

	
	V_N_A = VNA(dataFim,contract)
	y = PU_Par(V_N_A, j_emissao, x)
	
	plt.plot(x,y)
	plt.xlabel("Nº de Dias Uteis")
	plt.ylabel("Preço")
	plt.show()


if __name__ == '__main__':
	print("\n============== Contrato Base ==============")
	#nome_contrato = input("Digite o nome do contrato (Formato a ser escrito: '../contratoX.json'): ")
	nome_contrato = "../contratoX.json"
	dadosContrato = importar_contract(nome_contrato)

	print('\n')
	print("Identificador da operação (contract):", dadosContrato["contract"])
	print("Valor do PU de emissão da operação (emission_price):", dadosContrato["emission_price"])
	print("Data de emissão da operação (start_date):", dadosContrato["start_date"])
	print("Indexador da operação (index):", dadosContrato["index"])
	print("Taxa de juros da operação (spread):", dadosContrato["spread"])

	num_schedules = len(dadosContrato["schedules"])
	print("Quantidade de Schedules:",num_schedules)

	
	print("\n============== Entrar com Dados p/ Cálculo ==============")

	valorEmissao = dadosContrato["emission_price"]
	print("\nValor (PU) de emissão - Capital inicial emprestado (R$): ", valorEmissao)

	taxa_juros = dadosContrato["spread"]
	print("Spread - Taxa de juros a.a. (%): ",taxa_juros)


	# Data Digitada: digitar data de referência para o Cálculo
	dataCalculo = input("Digitar data desejada para a análise: ")
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
	jurosNegociacao = float(input("Digite taxa de juros para realização do negócio (em %): "))
	print("Juros Negociação:",jurosNegociacao,"%")
	#PU_Oper(somatorioJ, somatorioA, j_neg, du_i, du_j):
	print("PU Operacao:",PU_Oper(valorAtualizado, jurosNegociacao, numDiasUteis))

	print("\n============== Gráfico ==============")
	#resp = input("Deseja plotar grafico e acompanhar evolução dos preços? (S/N): ")
	resp = 'n'
	if (resp == 'S' or resp == 's'):
		plotarGrafico(dadosContrato)
	else:
		print("Encerrando codigo...")