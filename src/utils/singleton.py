def singleton(instance):
    instances = {}
    def impl(*args, **kw):
        if instance not in instances:
            instances[instance] = instance(*args, **kw)

        return instances[instance]

    return impl
