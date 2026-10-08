CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.raw_games (
    source       text        NOT NULL,  -- 'chesscom' o 'lichess'
    game_id      text        NOT NULL,  -- identificador de la partida en su plataforma
    played_month text        NOT NULL,  -- formato 'YYYY-MM', para la carga incremental
    payload      jsonb       NOT NULL,  -- la partida completa, sin modificar
    loaded_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (source, game_id)
);

-- Estado del ETL: hasta qué mes se cargó cada fuente.
CREATE TABLE IF NOT EXISTS etl_state (
    source     text        PRIMARY KEY,
    last_month text        NOT NULL,  -- formato 'YYYY-MM'
    updated_at timestamptz NOT NULL DEFAULT now()
);