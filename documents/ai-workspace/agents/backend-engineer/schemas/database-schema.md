# Database Schema Template

**Use this template for documenting new schema**

---

## Entity Name: [EntityName]

### Purpose
[What data does this entity represent?]

### Table Definition
```sql
CREATE TABLE [table_name] (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Core fields
    [field_1] [TYPE] [CONSTRAINTS],
    [field_2] [TYPE] [CONSTRAINTS],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT [name] CHECK ([condition]),
    FOREIGN KEY ([field]) REFERENCES [table]([field])
);
```

### Field Descriptions
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | INTEGER | No | Primary key |
| [field_1] | [TYPE] | [Yes/No] | [Description] |
| [field_2] | [TYPE] | [Yes/No] | [Description] |
| created_at | TIMESTAMP | No | Record creation time |
| updated_at | TIMESTAMP | No | Last update time |

### Indexes
```sql
-- Primary lookup index
CREATE INDEX idx_[table]_[column] 
    ON [table_name]([column1], [column2]);

-- Secondary index (if needed)
CREATE INDEX idx_[table]_[purpose] 
    ON [table_name]([column]);
```

### Common Queries
```sql
-- Query 1: [Description]
SELECT [fields] FROM [table_name] WHERE [condition];

-- Query 2: [Description]
SELECT [fields] FROM [table_name] WHERE [condition];
```

### Relationships
| Relation | Table | Type | Description |
|----------|-------|------|-------------|
| [name] | [table] | 1:N / N:1 / N:M | [Description] |

### Constraints & Rules
- [Constraint 1]
- [Constraint 2]

### Migration Notes
- [ ] Create table
- [ ] Add indexes
- [ ] Seed data (if any)
- [ ] Update related entities

---

## Implementation Checklist

- [ ] Schema designed
- [ ] Migration created
- [ ] Indexes added
- [ ] Queries tested
- [ ] Documentation updated
