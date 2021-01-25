from website_helpers.models import CalculatorResponse, Device, App, Route
from website_helpers import calculator

def handleRemoteForm(requestArgs):
    # Parameters
    device_count = int(requestArgs.get("deviceCount"))
    app_count = int(requestArgs.get("appCount"))

    devices = []
    for deviceIndex in range(1, device_count+1, 1):
        devices.append(Device(requestArgs, deviceIndex))

    apps = []
    for appIndex in range(1, app_count+1, 1):
        apps.append(App(requestArgs, appIndex))

    # FIXME: - Mocked

    devices, bandwidth = calculator.create_model(devices)

    remote_emissions = calculator.return_data(devices, bandwidth)

    remote_category = calculator.category(remote_emissions)

    model_response = CalculatorResponse(remote_category,remote_emissions, "TBI: Consumption Category", "TBI: CO2 Total emissions", "TBI: Difference CO2 emissions")

    return model_response.json()

def handleInPersonForm(requestArgs):
    # Parameters
    routes_count = int(requestArgs.get("destinationCount"))

    routes = []
    for routeIndex in range(1, routes_count+1, 1):
        routes.append(Route(requestArgs, routeIndex))

    # Pass data to model
    # FIXME: - Mocked
    model_response = CalculatorResponse("TBI: Consumption Category", "TBI: CO2 Total emissions", "TBI: Consumption Category", "TBI: CO2 Total emissions", "TBI: Difference CO2 emissions")

    return model_response.json()
