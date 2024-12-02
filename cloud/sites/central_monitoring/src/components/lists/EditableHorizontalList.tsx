import { useEffect, useState } from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Grid from '@mui/material/Grid';
import EditableListItem from '@/components/lists/EditableListItem';
import { LeftArrowIcon, RightArrowIcon } from '@/components/icons/ArrowIcon';

type ItemId = string;

type ItemType = { id: ItemId; name: string };

interface EditableHorizontalListProps<T extends ItemType> {
  items: T[];
  activeItem: ItemId | undefined;
  onItemPress: (id: ItemId) => void;
  editingActiveItem: boolean;
  onItemNameChange: (id: ItemId, name: string) => void;
  onFinishEditingItem: (id: ItemId, name: string) => void;
  hasError: Record<ItemId, boolean>;
}

const EditableBox = styled(Box)(({ theme }) => ({
  width: 128,
  height: 36,
  borderRadius: 8,
  '&.activeBox': {
    backgroundColor: theme.palette.primary.light,
  },
  '&.inactiveBox': {
    backgroundColor: theme.palette.background.inactive,
  },
  '&.editingErrorBox': {
    backgroundColor: '#FFF5F0',
    border: '4px solid #DE4038',
  },
  '&.errorBox': {
    backgroundColor: theme.palette.background.inactive,
    border: '1px solid #DE4038',
  },
}));

const EditableHorizontalList = <T extends ItemType>({
  items,
  activeItem,
  onItemPress,
  editingActiveItem,
  onItemNameChange,
  onFinishEditingItem,
  hasError,
}: EditableHorizontalListProps<T>) => {
  const [showScrollButtons, setShowScrollButtons] = useState(false);

  const handleScrollLeft = () => {
    const container = document.getElementById('list-container');
    if (container && container.scrollLeft > 0) {
      container.scrollTo({
        left: container.scrollLeft - 100,
        behavior: 'smooth',
      });
    }
  };

  const handleScrollRight = () => {
    const container = document.getElementById('list-container');

    if (container && container.offsetWidth + container.scrollLeft < container.scrollWidth) {
      container.scrollTo({
        left: container.scrollLeft + 100,
        behavior: 'smooth',
      });
    }
  };

  useEffect(() => {
    // Shows or hides scroll buttons depending on amount of elements in list
    const container = document.getElementById('list-container');
    if (container) {
      setShowScrollButtons(container.scrollWidth > container.clientWidth);
    }
  }, [items.length]);

  return (
    <Box sx={{ width: '100%', display: 'flex', alignItems: 'center' }}>
      <Box id='list-container' sx={{ overflowX: 'hidden', display: 'flex', gap: 16 }}>
        <List sx={{ display: 'flex', padding: 0, margin: 0 }}>
          {items.map((item) => (
            <ListItem
              key={item.id}
              sx={{ margin: (theme) => theme.spacing(0, 8, 0, 0), padding: 0 }}
              onClick={() => (activeItem !== item.id || !editingActiveItem) && onItemPress(item.id)}
            >
              <EditableBox
                className={
                  hasError[item.id]
                    ? activeItem === item.id && editingActiveItem
                      ? 'editingErrorBox'
                      : 'errorBox'
                    : activeItem === item.id
                    ? 'activeBox'
                    : 'inactiveBox'
                }
              >
                <EditableListItem
                  item={item}
                  isActive={item.id === activeItem}
                  isEditing={item.id === activeItem && editingActiveItem}
                  onNameChange={onItemNameChange}
                  hasError={hasError[item.id]}
                  onFinishEditing={onFinishEditingItem}
                />
              </EditableBox>
            </ListItem>
          ))}
        </List>
      </Box>
      {showScrollButtons && (
        <>
          <Grid
            display='flex'
            justifyContent='center'
            sx={{ minWidth: 48 }}
            onClick={handleScrollLeft}
          >
            <LeftArrowIcon />
          </Grid>
          <Grid
            display='flex'
            justifyContent='center'
            sx={{ minWidth: 48 }}
            onClick={handleScrollRight}
          >
            <RightArrowIcon />
          </Grid>
        </>
      )}
    </Box>
  );
};

export default EditableHorizontalList;
