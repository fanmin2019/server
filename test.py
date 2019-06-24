from models import User


def test_new():
    f = dict(
        username='min',
        password='123',
    )

    u = User.new(f)
    print('__dict__', u, type(u), u.__dict__, type(u.__dict__))
    u.save()
    print('test new', u)


def test_all():
    us = User.all()
    print('test all', us)


if __name__ == '__main__':
    test_new()
    test_all()