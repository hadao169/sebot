uwb_data = "1495[0.00,3.99,0.00]=2.74 CD37[0.00,0.00,0.00]=2.81 5B01[5.00,3.99,0.00]=3.66 592F[5.00,0.00,0.00]=3.68 le_us=3356 est[1.90,2.01,-0.20,95]"

anchor = uwb_data.rstrip().split()
measurement = {}
measurement["id"] = anchor[0:4]
xyz = anchor.split("[")[1].split("]")[0].split(",")
measurement["x"] = float(xyz[0])
measurement["y"] = float(xyz[1])
measurement["z"] = float(xyz[2])
measurement["range"] = float(anchor.split("=")[1])
print(measurement)