import ast, importlib.util, types, asyncio
from asyncio.futures import Future
from functools import wraps, partial
from typing import Coroutine, Callable

loop = asyncio.get_event_loop()


group_types = ("group", "supergroup")


def add_chat(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("INSERT INTO users (user_id) values (?)", (chat_id,))
        db.commit()
    elif chat_type in group_types:  # groups and supergroups share the same table
        dbc.execute(
            "INSERT INTO groups (chat_id,welcome_enabled) values (?,?)", (chat_id, True)
        )
        db.commit()
    elif chat_type == "channel":
        dbc.execute("INSERT INTO channels (chat_id) values (?)", (chat_id,))
        db.commit()
    else:
        raise TypeError("Unknown chat type '%s'." % chat_type)
    return True


def chat_exists(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("SELECT user_id FROM users where user_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    elif chat_type in group_types:  # groups and supergroups share the same table
        dbc.execute("SELECT chat_id FROM groups where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    elif chat_type == "channel":
        dbc.execute("SELECT chat_id FROM channels where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    else:
        raise TypeError("Unknown chat type '%s'." % chat_type)


def aiowrap(fn: Callable) -> Coroutine:
    @wraps(fn)
    def decorator(*args, **kwargs):
        wrapped = partial(fn, *args, **kwargs)

        return loop.run_in_executor(None, wrapped)

    return decorator


async def meval(code, local_vars):
    locs = {}
    globs = globals().copy()
    global_args = "_globs"
    while global_args in globs.keys():
        global_args = "_" + global_args
    local_vars[global_args] = {}
    for glob in ["__name__", "__package__"]:
        local_vars[global_args][glob] = globs[glob]

    root = ast.parse(code, "exec")
    code = root.body
    if isinstance(code[-1], ast.Expr):
        code[-1] = ast.copy_location(ast.Return(code[-1].value), code[-1])
    glob_copy = ast.Expr(
        ast.Call(
            func=ast.Attribute(
                value=ast.Call(
                    func=ast.Name(id="globals", ctx=ast.Load()), args=[], keywords=[]
                ),
                attr="update",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(arg=None, value=ast.Name(id=global_args, ctx=ast.Load()))
            ],
        )
    )
    ast.fix_missing_locations(glob_copy)
    code.insert(0, glob_copy)
    args = []
    for a in list(map(lambda x: ast.arg(x, None), local_vars.keys())):
        ast.fix_missing_locations(a)
        args += [a]
    args = ast.arguments(
        args=[],
        vararg=None,
        kwonlyargs=args,
        kwarg=None,
        defaults=[],
        kw_defaults=[None for i in range(len(args))],
    )
    if int.from_bytes(importlib.util.MAGIC_NUMBER[:-2], "little") >= 3410:
        args.posonlyargs = []
    fun = ast.AsyncFunctionDef(
        name="tmp", args=args, body=code, decorator_list=[], returns=None
    )
    ast.fix_missing_locations(fun)
    mod = ast.parse("")
    mod.body = [fun]
    comp = compile(mod, "<string>", "exec")

    exec(comp, {}, locs)

    r = await locs["tmp"](**local_vars)

    if isinstance(r, types.CoroutineType) or isinstance(r, Future):
        r = await r
    try:
        globals().clear()
    finally:
        globals().update(**globs)
    return r


def switch_case(switch, cases):
    if switch in cases:
        return cases[switch]
    elif "default_case" in cases:
        return cases["default_case"]
    else:
        return None
