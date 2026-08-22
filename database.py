import aiosqlite

DB_NAME = "bingo_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 20.0,
                referrals INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                referred_by INTEGER
            )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT balance, referrals, games_played FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def register_user(user_id, referred_by=None):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            if await cursor.fetchone():
                return False

        await db.execute("INSERT INTO users (user_id, balance, referred_by) VALUES (?, ?, ?)", (user_id, 20.0, referred_by))

        if referred_by:
            await db.execute("UPDATE users SET balance = balance + 10, referrals = referrals + 1 WHERE user_id = ?", (referred_by,))

        await db.commit()
        return True

async def increment_game(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET games_played = games_played + 1 WHERE user_id = ?", (user_id,))
        await db.commit()
