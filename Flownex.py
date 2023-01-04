#this flownex module is compatible with pythonnet
#tested on python 3.6
# Function to launch Flownex
def GetFlownexDirectory():
    import clr
    import Microsoft.Win32

    classesRoot = Microsoft.Win32.RegistryKey.OpenBaseKey(
        Microsoft.Win32.RegistryHive.ClassesRoot, Microsoft.Win32.RegistryView.Default)

    clsidRoot = classesRoot.OpenSubKey("CLSID")

    fnxKey = clsidRoot.OpenSubKey("{FD40D175-FED4-4619-8571-36336DD2B8E1}")

    if fnxKey is not None:
        localServerKey = fnxKey.OpenSubKey("LocalServer32")
        value = str(localServerKey.GetValue(None))
        value = value.replace(" /automation", "")
        value = value.rpartition('FlownexSE.exe')[0]
        return value

    return ""

def LaunchApplication():
    FlownexPath = GetFlownexDirectory()
    if FlownexPath != "":
        import clr
        clr.AddReference(FlownexPath + 'IPS.Core.dll')
        import IPS
        from IPS import Core
        IPS.Core.FlownexSEDotNet.InitialiseAssemblyResolver(FlownexPath)

        print("Launching Flownex from: " + FlownexPath)
        print("If this is the wrong version: Run registercomapi.bat as Administrator from a different Flownex install "
              "directory to change the Flownex version used by the API")
        FlownexSE = IPS.Core.FlownexSEDotNet.LaunchFlownexSE()
        return FlownexSE
    else:
        print("Flownex not registered for API use")
        print("Run registercomapi.bat as Administrator from the Flownex install directory to rectify this")

# Function to open a project
def OpenProject(FlownexApp, ProjectPath ):
    import IPS
    from IPS import Core
    FlownexApp.OpenProject(ProjectPath)
    FSEProject = FlownexApp.Project
    return FSEProject

def NewProject(FlownexApp, ProjectPath ):
    import IPS
    from IPS import Core
    FlownexApp.NewProject(ProjectPath)
    FSEProject = FlownexApp.Project
    return FSEProject


def SetupSimulationController(FSEProject):
    import IPS
    from IPS import Core
    SimulationController = IPS.Core.SimulationControlHelper(FSEProject)
    return SimulationController

def SetInput(FSEProject, Identifier, PropertyName, Value):
    import IPS
    from IPS import Core
    Element = IPS.Core.Element(FSEProject.GetElement(Identifier))
    Property = IPS.Core.Property(Element.GetPropertyFromFullDisplayName(PropertyName))
    Property.SetValueFromString(str(Value))
    return
def GetOutput(FSEProject, Identifier, PropertyName, propertyIsString=False):
    import IPS
    from IPS import Core
    Element = IPS.Core.Element(FSEProject.GetElement(Identifier))
    Property = IPS.Core.Property(Element.GetPropertyFromFullDisplayName(PropertyName))
    return Property.GetValueAsString()
def GetOutputUsingComponentDescription(FSEProject, PageName, ComponentDescription, PropertyName, propertyIsString=False):
    import IPS
    from IPS import Core
    from System.Collections.Generic import List
    ComponentList = List[IPS.Core.Component](FSEProject.Builder.GetComponentsOnPageUsingDescription(PageName, ComponentDescription))
    Component = IPS.Core.Component(ComponentList[0])
    Property = IPS.Core.Property(Component.GetPropertyFromFullDisplayName(PropertyName))
    return Property.GetValueAsString().replace("{COMPONENT}","")
def SolveSteadyState(SimulationController, time=5000.0):
    SimulationController.SolveSteadyStateAndWaitToComplete(time)
    return

def RunDesigner(FSEProject):
    FSEProject.RunDesigner()

    import time
    while True:
        time.sleep(0.5)
        if FSEProject.State == 1:
            return

def StepTransient(SimulationController):
    SimulationController.StepAndWaitToComplete()
    return

def StopTransient(SimulationController):
    SimulationController.StopAndWaitToComplete()
    return
	
def SaveProject(FlownexApp):
    FlownexApp.SaveProject()
    return
	
def CloseProject(FlownexApp):
    FlownexApp.CloseProject()
    return

def ExitApplication(FlownexApp):
    FlownexApp.Exit()
    return
	
def Disconnect(SimulationController):
    SimulationController.Disconnect()
    return