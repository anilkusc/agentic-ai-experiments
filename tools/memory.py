def remember(db, content):
    db.execute(
        "INSERT INTO memories (content) VALUES (?)",
        (content,)
    )
    db.commit()
    return {"status": "saved", "content": content}


def get_memories(db, limit):
    cursor = db.execute(
        """
        SELECT id, content, created_at
        FROM memories
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    return [
        {"id": row[0], "content": row[1], "created_at": row[2]}
        for row in cursor.fetchall()
    ]