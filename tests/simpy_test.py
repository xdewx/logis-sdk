import simpy

from logis.util.simpy_util import resize_container


def test_resize_container():
    env = simpy.Environment()
    container = simpy.Container(env, init=0, capacity=10)

    def get(n):
        print(f"get {n} start at {env.now}")
        yield container.get(n)
        print(f"get {n} end at {env.now}")

    def put(n):
        print(f"put {n} start at {env.now}")
        yield container.put(n)
        print(f"put {n} end at {env.now}")

    def resize_after(timeout: int, new_capacity: int):
        yield env.timeout(timeout)
        print(f"resize to {new_capacity} at {env.now}")
        resize_container(container, new_capacity)
        print(f"container capacity: {container.capacity}")

    def wait_request_done():
        while container.get_queue or container.put_queue:
            yield env.timeout(1)
            print(f"request not done, {env.now}")

    env.process(put(15))
    env.process(resize_after(5, 20))
    # env.process(wait_request_done())
    env.process(get(10))
    env.run()
    assert container.level == 5
