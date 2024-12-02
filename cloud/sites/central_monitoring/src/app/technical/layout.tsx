'use client';

interface RootLayoutProps {
  children: React.ReactNode;
}

const RootLayout = ({ children }: RootLayoutProps) => {
  return (
    <>
      <title>CMS - Home</title>
      {children}
    </>
  );
};

export default RootLayout;
