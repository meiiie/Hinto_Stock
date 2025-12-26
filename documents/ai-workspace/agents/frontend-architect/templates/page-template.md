# Page Template

**Use this template when creating new pages**

---

## Page Name: [PageName]

### URL Route
`/[route-path]`

### Purpose
[What does this page do? What user goal does it serve?]

### Layout
```
┌─────────────────────────────────────────────┐
│                   Header                    │
├─────────────────────────────────────────────┤
│                                             │
│              Main Content Area              │
│                                             │
├─────────────────────────────────────────────┤
│                   Footer                    │
└─────────────────────────────────────────────┘
```

### Components Used
| Component | Purpose | Location |
|-----------|---------|----------|
| Header | Navigation | Top |
| [Component1] | [Purpose] | [Location] |
| [Component2] | [Purpose] | [Location] |

### Data Requirements
| Data | Source | Refresh Rate |
|------|--------|--------------|
| [Data 1] | API endpoint | Real-time |
| [Data 2] | WebSocket | Real-time |
| [Data 3] | Cached | On mount |

### State Management
| State | Store | Description |
|-------|-------|-------------|
| [State 1] | Local | Component local state |
| [State 2] | Global | Zustand store |

### User Interactions
| Action | Trigger | Result |
|--------|---------|--------|
| [Action 1] | Button click | [Effect] |
| [Action 2] | Form submit | [Effect] |

### API Endpoints Used
| Endpoint | Method | When Called |
|----------|--------|-------------|
| /api/v1/[endpoint] | GET | On page load |
| /api/v1/[endpoint] | POST | On form submit |

### Loading States
- [ ] Initial page load skeleton
- [ ] Data refresh indicator
- [ ] Action loading feedback

### Error Handling
| Error Type | Display | Recovery |
|------------|---------|----------|
| Network error | Toast | Retry button |
| Validation | Inline | Fix and retry |
| Server error | Error page | Back button |

### Mobile Responsiveness
| Breakpoint | Layout Change |
|------------|---------------|
| Desktop (1280px+) | Full layout |
| Tablet (768px) | [Changes] |
| Mobile (640px) | [Changes] |

---

## Implementation Checklist

- [ ] Page component created
- [ ] Routing configured
- [ ] Data fetching implemented
- [ ] Loading states added
- [ ] Error handling complete
- [ ] Mobile responsive
- [ ] Tests written
- [ ] Documented
