import grequests

req_list = [grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_6_2021-05-11-22-05-50.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_6_2021-05-13-19-24-09.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_6_2021-05-11-22-01-42.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_7_2021-05-14-10-19-45.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_7_2021-05-13-23-22-44.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_7_2021-05-13-23-22-23.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_6_2021-05-11-22-00-26.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_7_2021-05-13-22-29-21.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_6_2021-05-13-19-52-43.onnx'),
grequests.get('http://xtra3090.d2.comp.nus.edu.sg/modelmarket_netron/provider_model_7_2021-05-13-22-35-58.onnx'),
]
res_list = grequests.map(req_list)
for i in range(len(res_list)):
    print(res_list[i].text)  # 打印第一个请求的响应文本