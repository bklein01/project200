from store.user import User
from store import ModelStore as DataStore
from game import Game
from core.dotdict import DotDict
from server import EventServer
import sys


def prnt(obj, k):
        def f(model, key, func):
            print obj + ':' + k + ' -> ' + model[k]
        return f


def server_main():
    print "Starting server..."
    EventServer.start()
    try:
        while True:
            if EventServer.has_events:
                event = EventServer.get_event()
                print str(event)
                if event.type is 'exit':
                    break
    except Exception as e:
        print e
    EventServer.stop()
    sys.exit(0)

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
