import time
    
def _rcall_recieve(payload):
    payload = eval(payload)

    function = globals()[payload['function']]
    callback = payload['callback']
    args = payload['payload'][0]
    kwargs = payload['payload'][1]

    response = function(*args, **kwargs)

    if callback:
        if type(response) == tuple:
            if len(response) == 2 and type(response[0]) == list and type(
                response[1]) == dict:
                _rcall_send(callback, response[0], response[1])
            else:
                _rcall_send(callback, list(response))
        elif type(response) == dict:
            _rcall_send(callback, [], response)
        elif type(response) == list:
            _rcall_send(callback, response)
        elif response is None:
            _rcall_send(callback)
        else:
            _rcall_send(callback, [response])

def _rcall_send(func, *args, **kwargs):
    callback, player = None, get_opponent()
    if 'callback' in kwargs:
        callback = kwargs['callback']
        del kwargs['callback']
    if 'player' in kwargs:
        player = kwargs['player']
        del kwargs['player']
    _rcall_send_ext(func, args, kwargs, callback, player)
    
def _rcall_send_ext(func, payload_list=None, payload_dict=None,
                    callback=None, player=None):
    if payload_list is None:
        payload_list = []
    if payload_dict is None:
        payload_dict = {}
    if player is None:
        player = get_opponent()
    try: func = func.__name__
    except AttributeError: pass
    try: callback = callback.__name__
    except AttributeError: pass

    payload = {'function':func, 'callback':callback,
               'payload':(payload_list,payload_dict)}

    remoteCall(player, '_rcall_recieve', str(payload).replace('"','\\"'))
    
def _rcall_wait(func, *args, **kwargs):
    timeout, player = None, get_opponent()
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
        del kwargs['timeout']
    if 'player' in kwargs:
        player = kwargs['player']
        del kwargs['player']
    _rcall_wait_ext(func, args, kwargs, timeout, player)
    
def _rcall_wait_ext(func, payload_list=None, payload_dict=None,
                    timeout=10, player=None):
    if payload_list is None:
        payload_list = []
    if payload_dict is None:
        payload_dict = {}
    if player is None:
        player = get_opponent()

    _rcall_send(func, payload_list, payload_dict, player)
    setGlobalVariable("network_lock", str(True))
    setGlobalVariable("reply_message", '')
    cur_time = time.clock()
    lock = eval(getGlobalVariable("network_lock"))

    # TODO: Test this more
    while lock:
        time.sleep(0.25)
        if time.clock()-cur_time >= timeout:
            raise TimeoutError()
        update()
        lock = eval(getGlobalVariable("network_lock"))
        if lock is False: break

    return getGlobalVariable("reply_message")
    
def _rcall_reply(message):
    setGlobalVariable("reply_message", str(message))
    setGlobalVariable("network_lock", str(False))