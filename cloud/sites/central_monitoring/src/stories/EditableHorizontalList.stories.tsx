import EditableHorizontalList from '@/components/lists/EditableHorizontalList';
import { action } from '@storybook/addon-actions';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof EditableHorizontalList> = {
  component: EditableHorizontalList,
};

export default meta;

type Story = StoryObj<typeof EditableHorizontalList>;

export const Default: Story = {
  args: {
    items: [
      { id: 'G1', name: 'Group 1' },
      { id: 'G2', name: 'Group 2' },
      { id: 'G3', name: 'Group 3' },
      { id: 'G4', name: 'Group 4' },
    ],
    activeItem: 'G2',
    onItemPress: action('onItemPress'),
    editingActiveItem: false,
    onItemNameChange: action('onItemNameChange'),
    onFinishEditingItem: action('onFinishEditingItem'),
    hasError: {},
  },
};

export const ItemError: Story = {
  args: {
    items: [
      { id: 'G1', name: 'Group 1' },
      { id: 'G2', name: 'Group 2' },
      { id: 'G3', name: 'Group 3' },
      { id: 'G4', name: 'Group 4' },
    ],
    activeItem: 'G2',
    editingActiveItem: false,
    onItemPress: action('onItemPress'),
    onItemNameChange: action('onItemNameChange'),
    onFinishEditingItem: action('onFinishEditingItem'),
    hasError: { G2: true },
  },
};

export const EditingActiveItem: Story = {
  args: {
    items: [
      { id: 'G1', name: 'Group 1' },
      { id: 'G2', name: 'Group 2' },
      { id: 'G3', name: 'Group 3' },
      { id: 'G4', name: 'Group 4' },
    ],
    activeItem: 'G2',
    editingActiveItem: true,
    onItemPress: action('onItemPress'),
    onItemNameChange: action('onItemNameChange'),
    onFinishEditingItem: action('onFinishEditingItem'),
    hasError: {},
  },
};

export const EditingActiveItemWithError: Story = {
  args: {
    items: [
      { id: 'G1', name: 'Group 1' },
      { id: 'G2', name: 'Group 2' },
      { id: 'G3', name: 'Group 3' },
      { id: 'G4', name: 'Group 4' },
    ],
    activeItem: 'G2',
    editingActiveItem: true,
    onItemPress: action('onItemPress'),
    onItemNameChange: action('onItemNameChange'),
    onFinishEditingItem: action('onFinishEditingItem'),
    hasError: { G2: true },
  },
};
