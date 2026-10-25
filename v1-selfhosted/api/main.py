from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.views import router as auth_router
from settings import settings
from sms.views import router as sms_router

from providers.simwood import router as simwood_router
from providers.sinch import router as sinch_router

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_methods=['*'], allow_headers=['*'], allow_credentials=False,
                   allow_origins=settings().CORS_ORIGINS)

app.include_router(auth_router, prefix='/api/auth')
app.include_router(simwood_router, prefix='/api/simwood')
app.include_router(sinch_router, prefix='/api/sinch')
app.include_router(sms_router, prefix='/api/sms')

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
