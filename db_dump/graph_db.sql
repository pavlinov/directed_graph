CREATE TABLE nodes (
    id VARCHAR PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE edges (
    id VARCHAR PRIMARY KEY,
    from_node VARCHAR REFERENCES nodes(id),
    to_node VARCHAR REFERENCES nodes(id),
    cost FLOAT DEFAULT 0 CHECK (cost >= 0) -- ensure non-negative costs
);

WITH RECURSIVE cycle_check(id, path, from_node, to_node, cycle) AS (
    SELECT
        e.id,
        ARRAY[e.from_node],
        e.from_node,
        e.to_node,
        CASE WHEN e.from_node = e.to_node THEN TRUE ELSE FALSE END
    FROM edges e

    UNION ALL

    SELECT
        e.id,
        path || e.from_node,
        e.from_node,
        e.to_node,
        CASE WHEN e.to_node = ANY(path) THEN TRUE ELSE FALSE END
    FROM edges e
    JOIN cycle_check cc ON e.from_node = cc.to_node
    WHERE NOT cycle
)
SELECT DISTINCT path || to_node AS cycle_path
FROM cycle_check
WHERE cycle;


WITH RECURSIVE cycle_check(id, path, from_node, to_node, cycle_detected) AS (
    SELECT
        e.id,
        ARRAY[e.from_node],
        e.from_node,
        e.to_node,
        CASE WHEN e.from_node = e.to_node THEN TRUE ELSE FALSE END
    FROM edges e

    UNION ALL

    SELECT
        e.id,
        path || e.from_node,
        e.from_node,
        e.to_node,
        CASE WHEN e.to_node = ANY(path) THEN TRUE ELSE FALSE END
    FROM edges e
    JOIN cycle_check cc ON e.from_node = cc.to_node
    WHERE NOT cycle_detected
),
cycles AS (
    SELECT path || to_node AS cycle_path
    FROM cycle_check
    WHERE cycle_detected
)
SELECT DISTINCT cycle_path
FROM cycles
WHERE (ARRAY_TO_STRING(cycle_path, ',')) LIKE (SELECT MIN(node) FROM UNNEST(cycle_path) s(node)) || '%';


-- Dijkstra's algorithm
WITH RECURSIVE
input_data AS (
  SELECT from_node, to_node, cost
  FROM edges
),
dijkstra AS (
  SELECT from_node, to_node, cost, ARRAY[to_node] AS path, cost AS total_cost
  FROM input_data
  WHERE from_node = 'a'  -- start node

  UNION ALL

  SELECT d.from_node, i.to_node, i.cost, path || i.to_node, total_cost + i.cost
  FROM input_data i
  JOIN dijkstra d ON d.to_node = i.from_node
  WHERE NOT path @> ARRAY[i.to_node]  -- avoid cycles
)
SELECT *
FROM dijkstra
WHERE to_node = 'e'  -- end node
ORDER BY total_cost
LIMIT 1;
