from website_helpers import ong_calculator as model
from datetime import date, timedelta

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
    if len(input_date) == 10 :
        tmp = "{}{}/{}{}/{}{}{}{}".format(input_date[8],input_date[9],input_date[5],input_date[6],input_date[0],input_date[1],input_date[2],input_date[3])
    else :
        tmp = "10/10/2018"
    date_of_purchase = date(*map(int, tmp.split('/')[::-1]))
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
    years_used = date_delta("2017/06/09")
    lifetime_hours = 5 * 260 * years_used
    screen_area = lenght_to_screen_area(16/9, 25)
    devices = [props.camera, props.plasma(screen_area), props.microphone] * 3
    devices += [props.high_codec, props.speaker, props.personal_comp]
    devices = [Device(d, lifetime_hours) for d in devices]
    devices += [Device(props.router, 2 * lifetime_hours)]

    bandwidth = 10 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    print_model(devices, bandwidth)
    return devices, bandwidth


def middle2_bound_model():
    props = model.ClientProperties
    years_used = date_delta("2017/06/09")
    lifetime_hours = 5 * 260 * years_used
    screen_area = lenght_to_screen_area(16/9, 25)
    devices = [props.camera, props.microphone]
    devices += [props.plasma(screen_area)] * 2
    devices += [props.speaker, props.personal_comp]
    devices = [Device(d, lifetime_hours) for d in devices]
    devices += [Device(props.router, lifetime_hours)]

    bandwidth = 5 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    print_model(devices, bandwidth)
    return devices, bandwidth


def middle1_bound_model():
    props = model.ClientProperties
    years_used = date_delta("2017/06/09")
    lifetime_hours = 5 * 260 * years_used
    screen_area = lenght_to_screen_area(16/9, 20)
    devices = [props.ledlcd(screen_area),props.microphone,props.personal_comp,props.router]
    devices = [Device(d, lifetime_hours) for d in devices]

    bandwidth = 1.5 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h

    print_model(devices, bandwidth)
    return devices, bandwidth


def lower_bound_model():
    props = model.ClientProperties
    years_used = date_delta("2017/06/09")
    lifetime_hours = 10 * 260 * years_used
    devices = [props.laptop, props.router]
    devices = [Device(d, lifetime_hours) for d in devices]
    bandwidth = 0.128 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    print_model(devices, bandwidth)
    return devices, bandwidth


def create_model(list_devices):                                                 #Input
    props = model.ClientProperties


    devices = []
    cnt_of_devices = 0

    for element in list_devices :
        years_used = date_delta(str(element.purchase_date))
        lifetime_hours = 10 * 260 * years_used

        if element.type == "laptop" :
            devices += [props.laptop]
        if element.type == "persComputer" :
            devices += [props.personal_comp]
        if element.type == "highCODEC" :
            devices += [props.high_codec]
        if element.type == "lowCODEC" :
            devices += [props.low_codec]
        if element.type == "projector" :
            devices += [props.projector]
        if element.type == "router" :
            devices += [props.router]
        if element.type == "camera" :
            devices += [props.camera]
        if element.type == "speaker" :
            devices += [props.speaker]
        if element.type == "micro" :
            devices += [props.microphone]
        if element.type == "screen" :
            screen_area = lenght_to_screen_area(int(element.inches), int(element.long)/int(element.large))
            if element.model == "plasma" :
                devices += [props.plasma(screen_area)]
            else :
                devices += [props.ledlcd(screen_area)]

        devices = [Device(devices[cnt_of_devices], lifetime_hours)]
        cnt_of_devices += 1

    bandwidth = 0.5 # Mb/s
    bandwidth *= 3600. / 1024 / 8 # Gb/h
    return devices, bandwidth


def print_model(devices, bandwidth):
    server_op = server_power(bandwidth)
    server_em = server_embodied_power(bandwidth)
    client_op = client_power(devices, "power")
    client_em = client_power(devices, "embodied_power")
    #print("Embodied", client_em, server_em, [s + client_em for s in server_em])
    #print("Operation", client_op, server_op, [s + client_op for s in server_op])
    total_low = client_op + client_em + server_op[0] + server_em[0]
    total_high = client_op + client_em + server_op[1] + server_em[1]
    print("CO2 (kg/hour):", model.energy_to_co2((total_low + total_high)/2))


def return_data(devices, bandwidth):
    server_op = server_power(bandwidth)
    server_em = server_embodied_power(bandwidth)
    client_op = client_power(devices, "power")
    client_em = client_power(devices, "embodied_power")

    total_low = client_op + client_em + server_op[0] + server_em[0]
    total_high = client_op + client_em + server_op[1] + server_em[1]

    return model.energy_to_co2(total_low + total_high / 2)

def category(remote_emissions):
    type_of_category = [0.23322969933143028, 2.1370573090129854, 6.685746235870748, 13.185258541950043]
    name_of_category = ["Lower class", "Lower middle class", "Upper middle class", "Upper class"]

    for i in range(0,len(type_of_category)) :
        type_of_category[i] = abs(type_of_category[i] - remote_emissions)

    closer_to_zero = type_of_category[0]
    for i in type_of_category :
        if i < closer_to_zero :
            closer_to_zero = i

    return name_of_category[type_of_category.index(closer_to_zero)]



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
