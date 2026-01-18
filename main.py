import uvicorn
from fastapi import FastAPI
from routes.get.router_get import router as get_router
from routes.post.router_post import router as post_router
from routes.put.router_put import router as put_router
from routes.delete.router_delete import router as delete_router
from routes.post.create_login import router as login_router
from routes.post.create_user import router as user_router
from routes.batch.router_batch import router as batch_router
from routes.analytics.router_analytics import router as analytics_router
from routes.excel.router_excel import router as excel_router
from database.connection_db import init_db

app = FastAPI()

init_db()

app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(batch_router)
app.include_router(analytics_router)
app.include_router(excel_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
