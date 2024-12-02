import { ReactElement, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import { LeftArrowIcon, RightArrowIcon } from '@/components/icons/ArrowIcon';

interface HorizontalListProps {
  children: ReactElement[];
}

const HorizontalListCustomItems = ({ children }: HorizontalListProps) => {
  const [showScrollButtons, setShowScrollButtons] = useState<boolean>(false);

  const handleScrollLeft = () => {
    const container = document.getElementById('horizontal-custom-list-container');
    if (container && container.scrollLeft > 0) {
      container.scrollTo({
        left: container.scrollLeft - 100,
        behavior: 'smooth',
      });
    }
  };

  const handleScrollRight = () => {
    const container = document.getElementById('horizontal-custom-list-container');

    if (container && container.offsetWidth + container.scrollLeft < container.scrollWidth) {
      container.scrollTo({
        left: container.scrollLeft + 100,
        behavior: 'smooth',
      });
    }
  };

  useEffect(() => {
    // Shows or hides scroll buttons depending on amount of elements in list
    const container = document.getElementById('horizontal-custom-list-container');
    if (container) {
      setShowScrollButtons(container.scrollWidth > container.clientWidth);
    }
  }, [children.length]);

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, display: 'flex', alignItems: 'center' }}>
      <Box
        id='horizontal-custom-list-container'
        sx={{ overflowX: 'hidden', display: 'flex', gap: 48 }}
      >
        {children}
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

export default HorizontalListCustomItems;
