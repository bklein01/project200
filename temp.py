from store.user import User
from store import DataStore
from game import Game
from core.dotdict import DotDict
from server import EventServer
from server.router import EventRouter
import sys


def prnt(obj, k):
        def f(model, key, func):
            print obj + ':' + k + ' -> ' + model[k]
        return f


def server_main():
    print "Starting server..."
    EventServer.start(log_level=10)
    try:
        EventRouter.listen_sync(EventServer)
    except KeyboardInterrupt:
        print '\nFinsihed.\n'
    return EventServer

def game_main():
    users = DotDict({
        'dave': User.new(None, 'dave', 'zimmed@zimmed.io', 'pwhashing', DataStore),
        'sally': User.new(None, 'sally', 'bitchtits@co.co', 'shit', DataStore),
        'ass': User.new(None, 'ass', 'assasss@ass', 'ass', DataStore),
        'anus': User.new(None, 'anus', 'anus@', 'anus', DataStore),
        'figgy': User.new(None, 'figgy', 'fig@', 'fig', DataStore)
    })
    g = Game.new(users.dave, DataStore)
    g.on_change('state', prnt('game', 'state'))
    g.add_player(users.sally, 1)
    g.add_player(users.ass, 2)
    g.add_player(users.anus, 3)
    g.new_game()
    g.on_change('table.state', prnt('table', 'state'))
    p = DotDict(dict((p.user.username, p.uid) for p in g.players))
    g.table.bet(p.sally, 50)
    g.table.bet(p.ass, 0)
    g.table.bet(p.anus, 55)
    g.table.bet(p.dave, 60)
    g.table.bet(p.sally, 0)
    g.table.bet(p.anus, 65)
    g.table.bet(p.dave, 0)
    return users, p, g

if __name__ == '__main__':
    main()
