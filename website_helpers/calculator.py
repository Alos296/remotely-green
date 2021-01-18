import ong_calculator as model
from datetime import date, timedelta

test = 5

def prepare_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--upper", default=False, action="store_true")
    parser.add_argument("-l", "--lower", default=False, action="store_true")
    parser.add_argument("-m1", "--middle1", default=False, action="store_true")
    parser.add_argument("-m2", "--middle2", default=False, action="store_true")
    parser.add_argument("-c", "--create", default=False, action="store_true")
    return parser


class Device():
    def __init__(self, device, lifetime_op_hours, use_factor=1):
        self.device = device
        self.lifetime_op_hours = lifetime_op_hours
        self.use_factor = use_factor

    @property
    def power(self):
        return self.device.power * self.use_factor * 1e-3

    @property
    def embodied_power(self):
        lifetime = self.lifetime_op_hours * 3600
        return self.use_factor * self.device.manufacture_energy / lifetime * 1e3

    @property
    def total_power(self):
        return self.power + self.embodied_power


def server_power(bandwidth):
    # kWh / GB
    power_low =  model.ServerProperties.energy_intensity_low
    power_high =  model.ServerProperties.energy_intensity_high
    return bandwidth * power_low, bandwidth * power_high


def server_embodied_power(bandwidth):
    power_low = model.ServerProperties.embodied_energy_intensity_low
    power_high = model.ServerProperties.embodied_energy_intensity_high
    return bandwidth * power_low, bandwidth * power_high


def client_power(devices, attr="total_power"):
    power = sum(map(lambda x: getattr(x, attr), devices))
    return power


def date_delta(input_date):
    today = date.today()
    date_of_purchase = date(*map(int, input_date.split('/')[::-1]))
    cnt = 0
    while today > date_of_purchase:
        date_of_purchase += timedelta(365)
        cnt += 1
    return cnt


def lenght_to_screen_area(format, size) :
    if format == 16/9 :
        h = (size/2) * 0.0254
        l = (8*size/9) * 0.0254
        return h * l

    if format == 4/3 :
        h = (3*size/5) * 0.0254
        l = (4*size/5) * 0.0254
        return h * l


def upper_bound_model():
    props = model.ClientProperties
    years_used = date_delta("28/8/2019")
    lifetime_hours = 5 * 260 * years_used
    screen_area = lenght_to_screen_area(16/9, 25)
    devices = [props.camera, props.plasma(screen_area), props.microphone] * 3
    devices += [props.high_codec, props.speaker, props.personal_comp]
    devices = [Device(d, lifetime_hours) for d in devices]
    devices += [Device(props.router, 2 * lifetime_hours)]

    bandwidth = 7 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    return devices, bandwidth


def middle2_bound_model():
    props = model.ClientProperties
    years_used = date_delta("28/8/2018")
    lifetime_hours = 5 * 260 * years_used
    screen_area = lenght_to_screen_area(16/9, 25)
    devices = [props.camera, props.microphone]
    devices += [props.plasma(screen_area)] * 2
    devices += [props.speaker, props.personal_comp]
    devices = [Device(d, lifetime_hours) for d in devices]
    devices += [Device(props.router, lifetime_hours)]

    bandwidth = 7 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    return devices, bandwidth


def middle1_bound_model():
    props = model.ClientProperties
    years_used = date_delta("28/8/2016")
    lifetime_hours = 5 * 260 * years_used
    screen_area = lenght_to_screen_area(16/9, 25)
    devices = [props.camera, props.ledlcd(screen_area), props.microphone]
    devices += [props.personal_comp]
    devices = [Device(d, lifetime_hours) for d in devices]
    devices += [Device(props.router, lifetime_hours)]

    bandwidth = 7 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    return devices, bandwidth


def lower_bound_model():
    props = model.ClientProperties
    years_used = date_delta("28/8/2013")
    lifetime_hours = 10 * 260 * years_used
    devices = [props.laptop, props.router]
    devices = [Device(d, lifetime_hours) for d in devices]
    bandwidth = 0.128 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    return devices, bandwidth


def create_model(list_devices):                                                 #Input
    props = model.ClientProperties


    devices = []
    cnt_of_devices = 0

    for element in list_devices :
        years_used = date_delta(element.purchase_date)

        lifetime_hours = 10 * 260 * years_used

        if element.type == "laptop" :
            devices += [props.laptop]
        if element.type == "personal computer" :
            devices += [props.personal_comp]
        if element.type == "high CODEC" :
            devices += [props.high_codec]
        if element.type == "low CODEC" :
            devices += [props.low_codec]
        if element.type == "projector" :
            devices += [props.projector]
        if element.type == "router" :
            devices += [props.router]
        if element.type == "camera" :
            devices += [props.camera]
        if element.type == "speaker" :
            devices += [props.speaker]
        if element.type == "microphone" :
            devices += [props.microphone]
        if element.type == "screen" :
            if element.model == "plasma" :
                screen_area = lenght_to_screen_area(element.inches, element.long/element.large)
                devices += [props.plasma(screen_area)]
            else :
                screen_area = lenght_to_screen_area(element.inches, element.long/element.large)
                devices += [props.ledlcd(screen_area)]

        devices = [Device(devices[cnt_of_devices], lifetime_hours)]
        cnt_of_devices += 1

    bandwidth = 0.128 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    return devices, bandwidth


def print_model(devices, bandwidth):
    server_op = server_power(bandwidth)
    server_em = server_embodied_power(bandwidth)
    client_op = client_power(devices, "power")
    client_em = client_power(devices, "embodied_power")
    print("Embodied", client_em, server_em, [s + client_em for s in server_em])
    print("Operation", client_op, server_op, [s + client_op for s in server_op])
    total_low = client_op + client_em + server_op[0] + server_em[0]
    total_high = client_op + client_em + server_op[1] + server_em[1]
    print("CO2 (kg/hour):", model.energy_to_co2(total_low), model.energy_to_co2(total_high))


def return_data(devices, bandwidth):
    server_op = server_power(bandwidth)
    server_em = server_embodied_power(bandwidth)
    client_op = client_power(devices, "power")
    client_em = client_power(devices, "embodied_power")

    total_low = client_op + client_em + server_op[0] + server_em[0]
    total_high = client_op + client_em + server_op[1] + server_em[1]

    return model.energy_to_co2(total_low + total_high / 2)



'''
    if not args.upper and not args.lower and not args.middle1 and not args.middle1 and not args.create :
        print("\nExit Failure\n")
        exit(0)

    if args.upper :
        devices, bandwidth = upper_bound_model()
        print("\n Upper model : \n")
        print_model(devices, bandwidth)

    if args.middle2 :
        print("\n Middle 2 model : \n")
        devices, bandwidth = middle2_bound_model()
        print_model(devices, bandwidth)

    if args.middle1 :
        print("\n Middle 1 model : \n")
        devices, bandwidth = middle1_bound_model()
        print_model(devices, bandwidth)

    if args.lower :
        devices, bandwidth = lower_bound_model()
        print("\n Lower model : \n")
        print_model(devices, bandwidth)

    if args.create :
        devices, bandwidth = create_model()
        print("\n Create model : \n")
        print_model(devices, bandwidth)
'''
