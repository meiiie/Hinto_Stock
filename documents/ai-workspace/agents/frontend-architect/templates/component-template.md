# Component Template

**Use this template when creating new UI components**

---

## Component Name: [ComponentName]

### Purpose
[What does this component do?]

### Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| prop1 | string | Yes | - | Description |
| prop2 | number | No | 0 | Description |

### Usage Example
```tsx
import { ComponentName } from '@/components/trading/ComponentName';

<ComponentName 
  prop1="value"
  prop2={10}
/>
```

### States
| State | Description | Visual |
|-------|-------------|--------|
| Default | Normal state | [Description] |
| Loading | Data loading | [Description] |
| Error | Error state | [Description] |
| Empty | No data | [Description] |

### Events
| Event | Payload | Description |
|-------|---------|-------------|
| onClick | - | When clicked |
| onChange | value: T | When value changes |

### Styling
- Uses design-system.md tokens
- Responsive: Yes/No
- Dark mode: Yes

### Accessibility
- [ ] Keyboard navigable
- [ ] Screen reader labels
- [ ] Focus indicators
- [ ] ARIA attributes

### Testing
- [ ] Unit tests written
- [ ] data-testid added
- [ ] Edge cases covered

---

## Implementation Checklist

- [ ] Component created
- [ ] Props typed
- [ ] Styles applied
- [ ] Tests written
- [ ] Documentation updated
