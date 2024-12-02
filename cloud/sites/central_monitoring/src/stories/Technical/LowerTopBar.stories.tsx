import LowerTopbar from '@/app/technical/home/LowerTopbar';
import { Meta, StoryObj } from '@storybook/react';
import { userEvent, screen } from '@storybook/testing-library';
import { expect, jest } from '@storybook/jest';

const meta: Meta<typeof LowerTopbar> = {
  title: 'Technical/Components/Topbar',
  component: LowerTopbar,
};

export default meta;
type Story = StoryObj<typeof LowerTopbar>;

export const Default: Story = {
  args: {},
  play: async () => {
    const removeItemSpy = jest.spyOn(Storage.prototype, 'removeItem');
    const LogoutButton = screen.getByTestId('logout-button');

    expect(LogoutButton).toBeInTheDocument();
    await userEvent.click(LogoutButton);
    expect(removeItemSpy).toBeCalledWith('accessToken');
    expect(removeItemSpy).toBeCalledWith('refreshToken');
    expect(removeItemSpy).toBeCalledWith('userType');
  },
};
