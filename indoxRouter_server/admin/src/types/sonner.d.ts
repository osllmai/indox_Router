declare module "sonner" {
  export function toast(message: string, options?: any): void;
  export const toast: {
    (message: string, options?: any): void;
    error(message: string, options?: any): void;
    success(message: string, options?: any): void;
    warning(message: string, options?: any): void;
    info(message: string, options?: any): void;
  };
  export function Toaster(): JSX.Element;
}
