_shadow_state = {}
_patch_list = {}

class _Global_State(dict):
    def __init__(self):
        super(self.__class__, self).__init__()
        # Setup static things here that don't need to be synched initially
        self.action_list = []
        self.turn_count = 0
        _shadow_state.update(self)
        # Setup more dynamic things here that will need to be synced

    def __getattr__(self, attr):
        try:
            return super(self.__class__, self).__getattr__(attr)
        except AttributeError:
            try:
                return self[attr]
            except KeyError:
                raise AttributeError("'{}' object has no attribute '{}'".format(
                    self.__class__.__name__, attr))

    def __setattr__(self, attr, value):
        self[attr] = value

    def _get_diff_patch(self):
        """
        Generates a diff patch between the global state and _shadow_state.
        :return diff:   Dict of Key => state.val
        """
        diff = {}
        for key in self.keys():
            if not _shadow_state.has_key(key):
                if type(self[key]) in (tuple,list,dict,set):
                    diff[key] = _copy(self[key])
                else:
                    diff[key] = self[key]
            elif self[key] != _shadow_state[key]:
                if type(self[key]) in (tuple,list,dict,set):
                    diff[key] = _copy(self[key])
                else:
                    diff[key] = self[key]
        return diff
        
g = _Global_State()

def sync():
    """
    Transmits a generated diff patch if changes were made, storing the patch
    for later confirmation.
    """
    diff_patch = g._get_diff_patch()
    if len(diff_patch) > 0:
        # id = str(uuid4())
        # _patch_list[id] = diff_patch
        # rcall_send(_sync_request, [id, diff_patch])
        try:
            confirmation = _rcall_wait(_sync_request, payload_dict=diff_patch)
            if confirmation == 'ok':
                _shadow_state.update(diff_patch)
        except TimeoutError:
            raise

def _sync_request(patch='{}'):
    """
    Recieves a request to apply a patch to the global state and sends
    confirmation if sucessful.

    :param id:       UUID of the recieved patch.
    :param patch:    String to be evaluated and patched.
    """
    patch = eval(patch)
    _shadow_state.update(patch)
    g.update(patch)
    # rcall_send(_sync_complete, [id])
    _rcall_reply('ok')
    sync()

def _sync_complete(id):
    """
    Recieved when a patch is confirmed and updates the shadow copy to reflect
    the change.

    :param id:    UUID of the confirmed patch.
    """
    _shadow_state.update(_patch_list[id])
    del(_patch_list[id])