import abc

from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    from .models import PykormModel

import kubernetes

def _custom_objects_api():
    return kubernetes.client.CustomObjectsApi()

class BaseQuery:
    baseobject: 'PykormModel' = None

    def __init__(self, baseobject: 'PykormModel'):
        self.baseobject = baseobject

    @abc.abstractmethod
    def _iter(self):
        raise Exception('Not implemented')

    def all(self):
        for el in self._iter():
            yield el



class NamespacedObjectQuery(BaseQuery):
    pass


class ClusterObjectQuery(BaseQuery):
    def _iter(self) -> Iterator['PykormModel']:
        api = _custom_objects_api()
        base_cls = self.baseobject

        objs = api.list_cluster_custom_object(base_cls._pykorm_group, base_cls._pykorm_version, base_cls._pykorm_plural)
        for obj in objs['items']:
            yield self.baseobject._instantiate_with_dict(obj)


    def _save(self, obj: 'PykormModel'):
        api = _custom_objects_api()

        k8s_dict = obj._k8s_dict

        if obj._k8s_uid == None:
            result = api.create_cluster_custom_object(obj._pykorm_group, obj._pykorm_version, obj._pykorm_plural, k8s_dict)
        else:
            result = api.patch_cluster_custom_object(obj._pykorm_group, obj._pykorm_version, obj._pykorm_plural, obj.name, k8s_dict)

        obj._set_attributes_with_dict(result)


    def _delete(self, obj: 'PykormModel'):
        api = _custom_objects_api()
        api.delete_cluster_custom_object(obj._pykorm_group, obj._pykorm_version, obj._pykorm_plural, obj.name)

