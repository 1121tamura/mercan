from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """
    ヘルスチェックAPI。

    バックエンドが正常に起動しているかを確認するためのエンドポイント。
    Electronアプリ起動時にバックエンドの準備完了を検知するために使用する。

    Returns:
        dict: {"status": "ok"}
    """
    return {"status": "ok"}
