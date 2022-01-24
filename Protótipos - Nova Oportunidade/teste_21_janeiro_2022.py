'''
PU Par x PU Oper 
Juros de emissão x Juros de negociação
	--> Juros de Emissão: 
		-é o que consta no contrato (campo spread no json) 
		-ele é o que corrige a debênture
	
	--> Juros de negociação: 
		-é um input externo dada a taxa que essa 
		operação seria negociada com um terceiro.
'''

'''
Seja o contrato X (ver arquivo JSON)
'''



def PU_Par(VNA, j_emi, du):
	'''Calculando Pu Par'''
	return VNA*(1 + (j_emi/100))**(du/252)

def PU_Oper(somatorioJ, somatorioA, j_neg, du_i, du_j):
	P = somatorioJ/((1 + (j_neg/100))**(du_i/252))
	Q = somatorioA/((1 + (j_neg/100))**(du_j/252))
	return P + Q

if __name__ == '__main__':
	print("#===== 01/01/2022 ====#")
	valorAtualizado = 1000
	print("VNA:",valorAtualizado)

	jurosEmissao = 10
	print("Juros emissao (em %):", jurosEmissao,"%")

	diasUteis=0
	print("Dias úteis:",diasUteis)
	print("Divisão dos dias uteis:",diasUteis/252)

	#PU_Par = VNA*(1+j_emi)**(du/252)
	print("PU Par:", PU_Par(valorAtualizado, jurosEmissao, diasUteis))

	#jurosNegociacao = float(input("Digite os juros de Negociacao (em %): "))
	jurosNegociacao = 5.0
	print("PU OPER:", PU_Oper(600, 550, 5, 252, 504))
	print("\n")
	'''
	print("#===== 01/01/2023 ====#")
	VNA = 1000
	print("VNA:",VNA)

	j_emi = 10/100
	print("Juros emissao:", j_emi)

	du=252
	print("Dias úteis:",du)
	print("Divisão dos dias uteis:",du/252)

	PU_Par = VNA*(1+j_emi)**(du/252)
	print("PU Par:", PU_Par)
	print("Juros completo:", 1100 - 1000)

	print("\n")

	print("#===== 01/01/2024 ====#")
	VNA = 1000
	print("VNA:",VNA)

	j_emi = 10/100
	print("Juros emissao:", j_emi)

	du=504
	print("Dias úteis:",du)
	print("Divisão dos dias uteis:",du/252)

	PU_Par = VNA*(1+j_emi)**(du/252)
	print("PU Par:", PU_Par)
	print("\n")
	'''