# -*- coding: utf-8 -*-

# pythonnet is required to run this script
# for detailed info on the functions used see the flownex API help file
# tested on python 3.6
import clr
import Flownex
import os
import time
import pandas as pd
import random
from tqdm import tqdm

page_name = "ICVs"
FileName = "ICVs_v1.5"

# set to True to use the Flownex instance that is already open for API function calls
# the "Use only one instance for all API clients" option must be enabled in Settings->Project->Application
useCurrentInstance = True


########################################################################################################################
#                                  define pre-configured API functions
########################################################################################################################

# Allows Python to remove files as Administrator
def remove_readonly(fn, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        fn(path)
    except Exception as exc:
        print("Skipped:", path, "because:\n", exc)


def addNode(name, x_pos, y_pos, view=False, viewName="View1"):
    if not view:
        FSEProject.Builder.AddComponentToPage(page_name, "Flownex.Components.Node", name, x_pos, y_pos, 15, 15, 0, 0)
    else:
        FSEProject.Builder.AddComponentViewOnPage(page_name, name, viewName, x_pos, y_pos, 15, 15, 0, 0)


def addBC(name, x_pos, y_pos):
    FSEProject.Builder.AddComponentToPage(page_name, "Flownex.Components.BoundaryCondition", name, x_pos, y_pos, 30,
                                          30, 0, 0)


def addBCP(name, x_pos, y_pos):
    FSEProject.Builder.AddComponentToPage(page_name, "Flownex.Components.BasicCentrifugalPump", name, x_pos, y_pos, 50, 50, 0, 0)


def addFlowRes(name, x_pos, y_pos):
    FSEProject.Builder.AddComponentToPage(page_name, "Flownex.Components.Resistance", name, x_pos, y_pos, 50, 50, 0, 0)


def addCHT(name, x_pos, y_pos):
    FSEProject.Builder.AddComponentToPage(page_name, "Flownex.Components.HeatTransfer", name, x_pos, y_pos, 50, 50, 0, 0)


def addTurbine(name, x_pos, y_pos):
    FSEProject.Builder.AddComponentToPage(page_name, "Flownex.Components.SimpleTurbine", name, x_pos, y_pos, 50, 50, 0, 0)


def addEfficiencyScript(name, x_pos, y_pos):
    FSEProject.Builder.AddComponentToPage(page_name, "Python Demo.Efficiency Script", name, x_pos, y_pos, 50, 50, 0, 0)


def linkComponents(name1, name2, view=False, fibre=False, data=False, viewName1="View1", viewName2="View1", fibreName="name", dataName1="Data1", dataName2="Data2", mult=1, const=0):
    if not data:
        if not view:
            if not fibre:
                FSEProject.Builder.LinkComponents(page_name, name1, name2)
            else:
                FSEProject.Builder.LinkComponents(page_name, name1, name2, fibreName)
        else:
            if not fibre:
                FSEProject.Builder.LinkComponentViews(page_name, name1, viewName1, name2, viewName2)
            else:
                FSEProject.Builder.LinkComponentViews(page_name, name1, viewName1, name2, viewName2, fibreName)
    else:
        FSEProject.Builder.DataTransferLinkComponents(page_name, name1, dataName1, name2, dataName2, mult, const)


########################################################################################################################
#                                  open Flownex and create drawing page
########################################################################################################################

#  we are going to use SizeF from System Drawing library of .net so we add a reference
clr.AddReference("System.Drawing")
from System.Drawing import SizeF
from System import String


CurrentFolder = os.path.dirname(os.path.realpath(__file__)) + "\\"

# open the flownex application

FlownexSE = Flownex.LaunchApplication()
# print(f'{CurrentFolder}{FileName}.proj')

FSEProject = Flownex.OpenProject(FlownexSE, f'{CurrentFolder}{FileName}.proj')

# open the newly copied project to start building
# if not useCurrentInstance:
#    FSEProject = Flownex.OpenProject(FlownexSE, f'{CurrentFolder}{FileName}.proj')
# else:
#    FSEProject = FlownexSE.Project  # use this if you want the API to use an already open instance of Flownex



SimulationController = Flownex.SetupSimulationController(FSEProject)


########################################################################################################################
#                                  Input definitions
########################################################################################################################

df_input =  pd.read_csv('./inputs/boundary_conditions.csv', index_col=0)[['WELL01_MA4_P', 'WELL01_MA_37', \
           'WELL01_MA4_T', 'WELL01_MA2_T', 'WELL01_MA_36',\
          ]]
df_input.dropna(inplace=True)
df_input.reset_index(inplace=True)

df_output = pd.DataFrame(columns=['P_Z0_before', 'P_Z0_after', 'P_Z1_before', 'P_Z1_after', 'P_WH_before', 'P_WH_after', 'T_Z0_before', 'T_Z0_after', 'T_Z1_before', 'T_Z1_after', \
							'top_icv_status_before', 'top_icv_status_after', 'bottom_icv_status_before', 'bottom_icv_status_after', \
							'P_bottom_before', 'P_bottom_after', 'T_WH_before', 'T_WH_after', 'command_type', 'failure'])


#########################################################################################################
#									Action Funcions 
#########################################################################################################

def SetTopICVLift(lift):
	top_icv_0_lift = str(lift).replace('.', ',')
	Flownex.SetInput(FSEProject, 'Top_ICV_0', "{Control Valve Loss Data}Valve lift / Fraction opening", top_icv_0_lift)

	# Considering communicating valve always open
	# top_icv_1_lift = str(random.random()).replace('.', ',')
	# Flownex.SetInput(FSEProject, 'Top_ICV_1', "{Control Valve Loss Data}Valve lift / Fraction opening", top_icv_1_lift)

def SetBottomICVLift(lift):
	bottom_icv_0_lift = str(lift).replace('.', ',')
	Flownex.SetInput(FSEProject, 'Bottom_ICV_0', "{Control Valve Loss Data}Valve lift / Fraction opening", bottom_icv_0_lift)
	
	# Considering communicating valve always open
	# bottom_icv_1_lift = str(random.random()).replace('.', ',')
	# Flownex.SetInput(FSEProject, 'Bottom_ICV_1', "{Control Valve Loss Data}Valve lift / Fraction opening", bottom_icv_1_lift)

def OpenTopICV(failure=False):

	global top_icv_status

	if failure:
		# 5% of times the valve does not respond to the command
		if random.random() < 0.05:
			SetTopICVLift(0)
			top_icv_status = False
			return 'Open_Top'
		else:
			SetTopICVLift(random.uniform(0.3, 0.7))
			top_icv_status = True
			return 'Open_Top'
	else:
		SetTopICVLift(1)
		top_icv_status = True
		return 'Open_Top'
	
	
def CloseTopICV(failure=False):
	
	global top_icv_status
	if failure:
		# 5% of times the valve does not respond to the command
		if random.random() < 0.05:
			SetTopICVLift(1)
			top_icv_status = True
			return 'Close_Top'
		else:
			SetTopICVLift(random.uniform(0.3, 0.7))
			top_icv_status = False
			return 'Close_Top'
	else:
		SetTopICVLift(0)
		top_icv_status = False
		return 'Close_Top'
	

def OpenBottomICV(failure=False):

	global bottom_icv_status
	if failure:
		# 5% of times the valve does not respond to the command
		if random.random() < 0.05:
			SetBottomICVLift(0)
			top_icv_status = False
			return 'Open_Bottom'
		else:
			SetBottomICVLift(random.uniform(0.3, 0.7))
			top_icv_status = True
			return 'Open_Bottom'
	else:
		SetBottomICVLift(1)
		bottom_icv_status = True
		return 'Open_Bottom'
	
	
def CloseBottomICV(failure=False):

	global bottom_icv_status
	if failure:
		# 5% of times the valve does not respond to the command
		if random.random() < 0.05:
			SetBottomICVLift(1)
			top_icv_status = True
			return 'Close_Bottom'
		else:
			SetBottomICVLift(random.uniform(0.3, 0.7))
			top_icv_status = False
			return 'Close_Bottom'
	else:
		SetBottomICVLift(0)
		bottom_icv_status = False
		return 'Close_Bottom'

	
def FormatDecimal(val):
	return str(val).replace('.', ',')

def SetBoundaryConditions(index):
	# index = random.choice(range(df_input.shape[0]))
	# print(f'{index} in dataset index: {index in df_input.index}')
	p_bottom = df_input['WELL01_MA4_P'].loc[index]

	# From exploratory data analysis, pressure differences on ICVs are:
	# Bottom ICV: ~20 kgf/cm²
	# Top ICV: ~50 kgf/cm²
	# Estimated error for pressure sensor: ~1% of full scale
	# Estimated error for temperature sensor: ~0.01% of full scale
	# Estimated pressure drop from ICV to downhole: ~50 kgf/cm²

	# Noise from exploratory data analysis
	P_Z0 = p_bottom + 100  + random.normalvariate(100, 6.314231)
	P_Z1 = p_bottom + 70 + random.normalvariate(70, 6.314231)

	P_WH = df_input['WELL01_MA_37'].loc[index] + random.normalvariate(0, 3.359756)

	T_Z0 = df_input['WELL01_MA4_T'].loc[index] + random.normalvariate(0, 1.554087)
	T_Z1 = df_input['WELL01_MA2_T'].loc[index] + random.normalvariate(0, 1.334842)


	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_0', "{Boundary Conditions}Pressure boundary condition", "Fixed on user total value")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_0', "{Boundary Conditions}Pressure", FormatDecimal(P_Z0) + " kg_force/cm²")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_0', "{Boundary Conditions}Temperature boundary condition", "Fixed on user value")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_0', "{Boundary Conditions}Temperature", FormatDecimal(T_Z0) + " °C")

	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_1', "{Boundary Conditions}Pressure boundary condition", "Fixed on user total value")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_1', "{Boundary Conditions}Pressure", FormatDecimal(P_Z1) + " kg_force/cm²")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_1', "{Boundary Conditions}Temperature boundary condition", "Fixed on user value")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Zone_1', "{Boundary Conditions}Temperature", FormatDecimal(T_Z1) + " °C")

	Flownex.SetInput(FSEProject, 'Boundary_Condition_Well_Head', "{Boundary Conditions}Pressure boundary condition", "Fixed on user total value")
	Flownex.SetInput(FSEProject, 'Boundary_Condition_Well_Head', "{Boundary Conditions}Pressure", FormatDecimal(P_WH) + " kg_force/cm²")

	return P_Z0, P_Z1, P_WH, T_Z0, T_Z1


#########################################################################################################
#									ICVs initial status
# 							True: Valve open / False: valve closed
#########################################################################################################
top_icv_status = True
bottom_icv_status = True
failure_prob = 0.5

for k in tqdm(range(10000)):
	print('--------------------------------------------------------------------------------------------')
	print(f'Top ICV status: {top_icv_status}, Bottom ICV status: {top_icv_status}')
	print(f'Iteration {k}')

	####################################################
	# Getting all the conditions before any valve action
	####################################################

	top_icv_status_before = top_icv_status
	bottom_icv_status_before = bottom_icv_status

	# Randomly choose a point in a sample dataset
	index = random.choice(range(df_input.shape[0]))
	# Insert inherent randomness of the process	
	P_Z0_before, P_Z1_before, P_WH_before, T_Z0_before, T_Z1_before = SetBoundaryConditions(index)

	# failure = False

	supposed_action = random.choices([True, False])[0]

	# Run simulation without any valve action
	Flownex.SolveSteadyState(SimulationController, 5000.0)

	p_out = Flownex.GetOutput(FSEProject, 'P_out', "{Flow Node Results}Total pressure")
	print(f'Downhole pressure before: {p_out}')

	t_out = Flownex.GetOutput(FSEProject, 'T_WH', "{Flow Node Results}Total temperature")
	print(f'Temperature on wellhead before: {t_out}')

	P_bottom_before = p_out.split()[0].replace(',', '.')
	T_WH_before = t_out.split()[0].replace(',', '.')

	command_type = 'No-action'

	# df_aux = pd.DataFrame([[P_Z0, P_Z1, P_WH, T_Z0, T_Z1, \
							# top_icv_status, bottom_icv_status, failure, P_bottom, T_WH, command_type]], \
							# columns=['P_Z0', 'P_Z1', 'P_WH', 'T_Z0', 'T_Z1', \
							# 'top_icv_status', 'bottom_icv_status', 'failure', 'P_bottom', 'T_WH', 'Type'])
	# print(df_aux)

	# df_output = pd.concat([df_output, df_aux])


	# Setting valve action (failure or not)
	failure = random.choices([True, False], weights=[failure_prob, 1-failure_prob])[0]
	print(f'Failure: {failure}')
	print(f'Supposed action: {supposed_action}')


	if supposed_action:
		print('########### Supposed to action #############')
		if top_icv_status and bottom_icv_status:
			possible_actions = [CloseTopICV, CloseBottomICV]
			# Randomly executing one of the possible actions in the current state
			command_type = random.choice(possible_actions)(failure)

		elif top_icv_status and not bottom_icv_status:
			command_type = OpenBottomICV(failure)

		elif not top_icv_status and bottom_icv_status:
			command_type = OpenTopICV(failure)

	else:
		print('*********** Not supposed to action ***************')
		if failure:
			if top_icv_status and bottom_icv_status:
				possible_actions = [CloseTopICV, CloseBottomICV]
				# Randomly executing one of the possible actions in the current state
				command_type = random.choice(possible_actions)()

			elif top_icv_status and not bottom_icv_status:
				command_type = OpenBottomICV()

			elif not top_icv_status and bottom_icv_status:
				command_type = OpenTopICV()

		# elif not top_icv_status and not bottom_icv_status:


	####################################################
	# Getting all the conditions after any valve action
	####################################################
	top_icv_status_after = top_icv_status
	bottom_icv_status_after = bottom_icv_status
		
	# Insert inherent randomness of the process again and rerun the simulation
	P_Z0_after, P_Z1_after, P_WH_after, T_Z0_after, T_Z1_after = SetBoundaryConditions(index)
	Flownex.SolveSteadyState(SimulationController, 5000.0)


	p_out = Flownex.GetOutput(FSEProject, 'P_out', "{Flow Node Results}Total pressure")
	print(f'Downhole pressure after: {p_out}')

	t_out = Flownex.GetOutput(FSEProject, 'T_WH', "{Flow Node Results}Total temperature")
	print(f'Temperature on wellhead after: {t_out}')

	P_bottom_after = p_out.split()[0].replace(',', '.')
	T_WH_after = t_out.split()[0].replace(',', '.')

	df_aux = pd.DataFrame([[P_Z0_before, P_Z0_after, P_Z1_before, P_Z1_after, P_WH_before, P_WH_after, T_Z0_before, T_Z0_after, T_Z1_before, T_Z1_after, \
							top_icv_status_before, top_icv_status_after, bottom_icv_status_before, bottom_icv_status_after, \
							P_bottom_before, P_bottom_after, T_WH_before, T_WH_after, command_type, failure]], \
							columns=['P_Z0_before', 'P_Z0_after', 'P_Z1_before', 'P_Z1_after', 'P_WH_before', 'P_WH_after', 'T_Z0_before', 'T_Z0_after', 'T_Z1_before', 'T_Z1_after', \
							'top_icv_status_before', 'top_icv_status_after', 'bottom_icv_status_before', 'bottom_icv_status_after', \
							'P_bottom_before', 'P_bottom_after', 'T_WH_before', 'T_WH_after', 'command_type', 'failure'])
	print(df_aux)

	df_output = pd.concat([df_output, df_aux])
	

Flownex.Disconnect(SimulationController)
Flownex.SaveProject(FlownexSE)

df_output.reset_index(inplace=True, drop=True)
print(df_output.info())
df_output.to_csv('./outputs/synthetic_failure_data.csv')