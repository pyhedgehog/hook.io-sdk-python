import weakref
from .utils import opt_json

roles = [
    'datastore::del',
    'datastore::get',
    'datastore::recent',
    'datastore::set',
    'domain::create',
    'domain::destroy',
    'domain::find',
    'domain::get',
    'domain::update',
    'env::read',
    'env::write',
    'events::read',
    'events::write',
    'files::createReadStream',
    'files::createWriteStream',
    'files::download',
    'files::readFile',
    'files::readdir',
    'files::removeFile',
    'files::stat',
    'files::upload',
    'files::writeFile',
    'hook::create',
    'hook::destroy',
    'hook::find',
    'hook::logs::read',
    'hook::logs::write',
    'hook::package::read',
    'hook::presenter::read',
    'hook::resource::read',
    'hook::run',
    'hook::source::read',
    'hook::update',
    'hook::view::read',
    'keys::checkAccess',
    'keys::create',
    'keys::destroy',
    'keys::read',
]


class Keys:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def checkAccess(self, data, raw=False, **opts):
        opts.setdefault('json_auth', True)
        r = self.client.request('POST', 'keys/checkAccess', data, **opts)
        return opt_json(r, raw)

    def create(self, name, data, raw=False, **opts):
        data['name'] = name
        opts.setdefault('json_auth', True)
        # opts.setdefault('json_forbid', True)
        r = self.client.request('POST', 'keys/create', data, **opts)
        return opt_json(r, raw)

    def destroy(self, name, raw=False, **opts):
        opts.setdefault('json_auth', True)
        r = self.client.request('POST', 'keys/destroy', {'name': name}, **opts)
        return opt_json(r, raw)

    def all(self, raw=False, **opts):
        opts.setdefault('json_auth', True)
        r = self.client.request('POST', 'keys/all', {}, **opts)
        return opt_json(r, raw)

    def info(self, check_key=None, hook_private_key=None, **opts):
        if hook_private_key is None:
            hook_private_key = self.client.hook_private_key
        if check_key is None:
            check_key = hook_private_key
        opts['hook_private_key'] = hook_private_key
        for bad in 'raw anonymous streaming'.split():
            if bad in opts:
                del opts[bad]
        for info in self.all(**opts):
            if info['hook_private_key'] == check_key:
                return info


if __name__=='__main__':
    print('\n'.join(roles))
