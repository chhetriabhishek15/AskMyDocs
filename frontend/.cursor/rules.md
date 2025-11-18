# Frontend Cursor Rules

## React Patterns

1. **Functional Components Only**: Use function components with hooks, no class components
2. **TypeScript Required**: All files must be `.tsx` or `.ts`, no `.js` files
3. **Component Structure**: One component per file, export as default
4. **Atomic Design**: Build small, reusable components
5. **Props Interface**: Define props interface/type above component

## Hooks Usage

1. **React Query**: Use for all API calls (no direct fetch/axios in components)
2. **Custom Hooks**: Extract reusable logic into custom hooks
3. **Dependency Arrays**: Always include correct dependencies in useEffect, useMemo, useCallback
4. **Memoization**: Use `useMemo` for expensive computations, `useCallback` for function props

## State Management

1. **React Query**: Use for server state (caching, background refetch)
2. **Local State**: Use `useState` for UI-only state
3. **Context**: Use sparingly, only for truly global state
4. **No Redux**: Do not use Redux unless explicitly required

## API Integration

1. **React Query Mutations**: Use for POST/PUT/DELETE operations
2. **React Query Queries**: Use for GET operations
3. **Deduplication**: React Query handles request deduplication automatically
4. **Error Handling**: Use React Query's error handling, display user-friendly messages
5. **Loading States**: Use `isLoading` and `isFetching` appropriately

## Component Patterns

1. **File Upload**: Use `react-dropzone` for drag-and-drop
2. **Forms**: Use controlled components, validate with TypeScript types
3. **Lists**: Use proper keys, virtualize if needed for large lists
4. **Modals**: Use portals for modals, handle focus management

## Styling

1. **Tailwind CSS**: Use Tailwind for all styling
2. **Responsive**: Mobile-first approach
3. **Dark Mode**: Support dark mode if needed
4. **Accessibility**: Use semantic HTML, ARIA labels where needed

## Performance

1. **Code Splitting**: Use React.lazy for route-based code splitting
2. **Memo**: Use React.memo for components that receive stable props
3. **Avoid Re-renders**: Check React DevTools Profiler for unnecessary re-renders
4. **Bundle Size**: Monitor bundle size, use dynamic imports for large libraries

## File Organization

```
src/
├── components/     # Reusable UI components
├── pages/          # Page components
├── hooks/          # Custom React hooks
├── api/            # API client functions
├── utils/          # Utility functions
├── types/          # TypeScript type definitions
└── styles/         # Global styles, Tailwind config
```

## TypeScript

1. **Strict Mode**: Always use strict TypeScript settings
2. **No Any**: Avoid `any` type, use `unknown` if type is truly unknown
3. **Interfaces vs Types**: Use interfaces for object shapes, types for unions/intersections
4. **Generic Types**: Use generics for reusable components/hooks

## Testing (Future)

1. **React Testing Library**: Use for component tests
2. **Vitest**: Use for unit tests
3. **MSW**: Use Mock Service Worker for API mocking
4. **Test Coverage**: Aim for 80%+ coverage

## Code Quality

1. **ESLint**: Follow ESLint rules, fix all warnings
2. **Prettier**: Use Prettier for code formatting
3. **Import Order**: Standard library → third-party → local imports
4. **Naming**: Use PascalCase for components, camelCase for functions/variables

## Common Patterns

### API Call Pattern
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['resource', id],
  queryFn: () => api.getResource(id),
});
```

### Mutation Pattern
```typescript
const mutation = useMutation({
  mutationFn: api.createResource,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['resources'] });
  },
});
```

### Component Pattern
```typescript
interface ComponentProps {
  id: string;
  onAction: (value: string) => void;
}

const Component: React.FC<ComponentProps> = ({ id, onAction }) => {
  // Component logic
  return <div>...</div>;
};

export default Component;
```

