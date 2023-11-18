def profile(func):
    import io
    import time
    import pstats
    import cProfile
    from pstats import SortKey

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        value = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        with open('profile.log', 'w') as f:
            f.write(s.getvalue())
        # print(s.getvalue())
        return value
    return inner
