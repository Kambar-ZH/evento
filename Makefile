start-local:
	uvicorn evento.main:app --reload

migration-create:
	alembic revision --autogenerate -m "$(name)"

migration-run:
	alembic upgrade head

enter-db:
	docker exec -it postgres psql -U postgres fastapi