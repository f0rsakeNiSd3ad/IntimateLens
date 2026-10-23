import { cn } from "@/lib/utils";

export const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <div className={cn("rounded-lg border bg-card p-6 shadow-sm", className || "")}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <div className={cn("flex flex-col space-y-2 text-sm font-medium", className || "")}>
      {children}
    </div>
  );
};

export const CardTitle = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <h3 className={cn("font-semibold leading-none tracking-tight", className || "")}>
      {children}
    </h3>
  );
};

export const CardContent = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <div className={cn("mt-2 text-sm text-muted-foreground", className || "")}>
      {children}
    </div>
  );
};