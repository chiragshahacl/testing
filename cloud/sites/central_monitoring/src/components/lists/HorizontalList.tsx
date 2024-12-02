import { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import { LeftArrowIcon, RightArrowIcon } from '@/components/icons/ArrowIcon';
import { GroupType } from '@/types/group';

interface HorizontalListProps {
  items: GroupType[];
  activeItem: string;
  setActiveItem: (group: string) => void;
}

const HorizontalList = ({ items, activeItem, setActiveItem }: HorizontalListProps) => {
  const [showScrollButtons, setShowScrollButtons] = useState<boolean>(false);

  const handleScrollLeft = () => {
    const container = document.getElementById('horizontal-list-container');
    if (container && container.scrollLeft > 0) {
      container.scrollTo({
        left: container.scrollLeft - 100,
        behavior: 'smooth',
      });
    }
  };

  const handleScrollRight = () => {
    const container = document.getElementById('horizontal-list-container');

    if (container && container.offsetWidth + container.scrollLeft < container.scrollWidth) {
      container.scrollTo({
        left: container.scrollLeft + 100,
        behavior: 'smooth',
      });
    }
  };

  useEffect(() => {
    // Shows or hides scroll buttons depending on amount of elements in list
    const container = document.getElementById('horizontal-list-container');
    if (container) {
      setShowScrollButtons(container.scrollWidth > container.clientWidth);
    }
  }, [items.length]);

  return (
    <Box sx={{ width: '100%', display: 'flex', alignItems: 'center' }}>
      <Box id='horizontal-list-container' sx={{ overflowX: 'hidden', display: 'flex', gap: 16 }}>
        <List sx={{ display: 'flex', padding: 0, margin: 0 }}>
          {items.map((item) => (
            <ListItem
              key={item.id}
              sx={{ margin: 0, padding: 0 }}
              onClick={() => setActiveItem(item.id)}
            >
              <Button
                key={item.id}
                size='small'
                className={item.id === activeItem ? '' : 'unselected'}
                variant='contained'
                sx={{
                  whiteSpace: 'nowrap',
                  minWidth: 'auto',
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  },
                }}
              >
                {item.name}
              </Button>
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

export default HorizontalList;
